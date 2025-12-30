import os

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings

from .forms import AnalysisUploadForm
from .models import Analysis
from .services.conar_engine import analyze_conar_image_from_file

def _absolute_image_url(request, analysis: Analysis) -> str:
    """
    Build an absolute URL for the uploaded image.
    In local dev, this will be http://127.0.0.1:8000/media/...
    In production, you want a public URL (S3/R2) or proper host config.
    """
    return request.build_absolute_uri(analysis.image.url)

def upload_and_analyze(request):
    if request.method == "POST":
        form = AnalysisUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # 1. Save to DB first to generate file path
                analysis: Analysis = form.save(commit=False)
                analysis.save()
                print(f"DEBUG [Analysis {analysis.pk}]: Saved to DB. Image: {analysis.image.path}")

                # 2. Prepare for analysis
                model = os.getenv("OPENAI_MODEL", "gpt-4o")
                image_path = analysis.image.path

                # 3. Call AI Engine
                service_response = analyze_conar_image_from_file(
                    image_path=image_path,
                    model=model,
                )
                
                result = service_response.get("result", {})
                image_data_url = service_response.get("image_data_url")

                # Inject data URL into the result so frontend can use it even if file is gone
                if image_data_url:
                    result["cached_image_url"] = image_data_url
                
                # 4. Success handling
                analysis.global_status = result.get("global", {}).get("status", "yellow")
                analysis.result_json = result
                analysis.save()
                return redirect(reverse("analysis_detail", kwargs={"pk": analysis.pk}))

            except Exception as e:
                # Log the full error to Railway console
                print("CRITICAL ERROR IN ANALYZE VIEW:")
                import traceback
                traceback.print_exc()

                # If analysis exists, try to update it with the error
                if 'analysis' in locals() and analysis.pk:
                    analysis.global_status = "yellow"
                    analysis.result_json = {
                        "global": {
                            "status": "yellow",
                            "summary": "System Error during analysis.",
                        },
                        "cards": [{
                            "id": "error",
                            "title": "Erro de Sistema",
                            "status": "red",
                            "findings": [{
                                "severity": "high",
                                "what": "Falha no processamento",
                                "why": f"Erro interno: {str(e)}",
                                "fix": "Verifique os logs do servidor."
                            }]
                        }]
                    }
                    try:
                        analysis.save()
                        return redirect(reverse("analysis_detail", kwargs={"pk": analysis.pk}))
                    except:
                        # If we can't even save the error state, fall through
                        pass
                
                # Fallback if DB save failed or update failed
                form.add_error(None, f"Ocorreu um erro interno: {str(e)}")
    else:
        form = AnalysisUploadForm()

    return render(request, "analyzer/upload.html", {"form": form})

def analysis_detail(request, pk: int):
    analysis = get_object_or_404(Analysis, pk=pk)
    result = analysis.result_json or {}
    cards = result.get("cards", [])
    global_data = result.get("global", {})

        request,
        "analyzer/detail.html",
        {"analysis": analysis, "global_data": global_data, "cards": cards, "result": result},
    )

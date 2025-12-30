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
            analysis: Analysis = form.save(commit=False)
            analysis.save()  # save first so image has a URL

            model = os.getenv("OPENAI_MODEL", "gpt-4o")
            image_path = analysis.image.path

            try:
                result = analyze_conar_image_from_file(
                    image_path=image_path,
                    model=model,
                )
                analysis.global_status = result.get("global", {}).get("status", "yellow")
                analysis.result_json = result
            except Exception as e:
                # Fail-safe: store an actionable error in the same schema-ish shape
                analysis.global_status = "yellow"
                analysis.result_json = {
                    "global": {
                        "status": "yellow",
                        "summary": "Analysis failed. Please try again or verify image accessibility.",
                    },
                    "cards": [
                        {
                            "id": "conar",
                            "title": "CONAR (Brasil) – Advertising Self-Regulation",
                            "status": "yellow",
                            "checks": {
                                "has_18_plus_warning": False,
                                "has_responsible_gambling": False,
                                "mentions_easy_money": False,
                                "targets_minors": False,
                                "glamorizes_wealth": False,
                                "uses_urgency_pressure": False,
                                "minimizes_risk": False,
                            },
                            "findings": [
                                {
                                    "severity": "medium",
                                    "what": "Erro ao processar a análise automática.",
                                    "why": f"A ferramenta não conseguiu acessar/analisar a imagem. Detalhe: {str(e)[:160]}",
                                    "fix": "Tente novamente. Se estiver em produção, garanta que a imagem esteja em URL pública (ex: S3/R2).",
                                }
                            ],
                        }
                    ],
                }

            analysis.save()
            return redirect(reverse("analysis_detail", kwargs={"pk": analysis.pk}))
    else:
        form = AnalysisUploadForm()

    return render(request, "analyzer/upload.html", {"form": form})

def analysis_detail(request, pk: int):
    analysis = get_object_or_404(Analysis, pk=pk)
    result = analysis.result_json or {}
    cards = result.get("cards", [])
    global_data = result.get("global", {})

    return render(
        request,
        "analyzer/detail.html",
        {"analysis": analysis, "global_data": global_data, "cards": cards},
    )

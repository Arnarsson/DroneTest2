from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/embed", tags=["embed"])

@router.get("/snippet", response_class=HTMLResponse)
def embed_snippet(
    min_evidence: int = Query(2, ge=1, le=4),
    country: str | None = Query(None),
    height: int = Query(500, ge=300, le=2000)
):
    params = f"minEvidence={min_evidence}"
    if country:
        params += f"&country={country}"

    html = f"""
    <!-- DroneWatch Embed -->
    <iframe
      src="https://dronewatch.cc/embed/map?{params}"
      width="100%"
      height="{height}"
      style="border:0;overflow:hidden"
      loading="lazy"
      referrerpolicy="no-referrer-when-downgrade"
      ></iframe>
    """
    return HTMLResponse(content=html.strip())

@router.get("/js", response_class=HTMLResponse)
def embed_js():
    js = """
    <!-- DroneWatch JS Widget -->
    <script>
    (function() {
      var container = document.currentScript.parentElement;
      var iframe = document.createElement('iframe');
      iframe.src = 'https://dronewatch.cc/embed/map?minEvidence=2';
      iframe.width = '100%';
      iframe.height = '500';
      iframe.style.border = '0';
      iframe.loading = 'lazy';
      container.appendChild(iframe);
    })();
    </script>
    """
    return HTMLResponse(content=js.strip())
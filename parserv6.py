# -*- coding: utf-8 -*-
print("**Python Markdown parser - md-pypage - converts multiple Markdown files to Website**")
print("**Written by Lars Müller alias LMD or appgurueu in Python 3.5 - requires Python >= 3.2**")
#from cgi import html
from xml.sax.saxutils import escape, unescape
import urllib.parse as parse
from os import walk
from os.path import splitext, join
import math

html_escape_table = {
    '"': "&quot;",
    "'": "&apos;"
}

def html_escape(text):
    return escape(text, html_escape_table)

def img(alt,url,title):
    return """<img class="img-fluid" src=\""""+url+"""\" alt=\""""+alt+"""\"><div class="caption">"""+parse_markdown(title[1:-1])+"""</div>"""

def parse_markdown(string,parent=False,parent_quote=False,subquote=0): # PARSES A SINGLE LINE !
    global liste
    global ID
    global headers
    global quote
    suffix=""
    prefix=""
    if string.find("*") != -1 and (string[0:string.find("*")].count(" ") == string.find("*")) and not (parent or string[string.find("*")+1]=="*"): # LISTS
        prevliste=liste
        liste=1+int(string.find("*")/3)
        if (liste > prevliste):
            for i in range(0,liste-prevliste):
                prefix+="<ul>"
        elif (liste < prevliste):
            for i in range(0,prevliste-liste):
                prefix+="</ul>"
        return prefix+"<li>"+parse_markdown(string[string.find("*")+2:],parent=True)+"</li>"+suffix
    if not parent and liste != 0 and string=="":
        for i in range(0,liste):
            prefix+="</ul>"
        liste=0
    if len(string) > 2 and string[0:2]=="> ":
        curquote=1
        string=string[2:]
        while len(string) > 2 and string[0:2]=="> ":
            string=string[2:]
            curquote+=1
        for i in range(quote,curquote):
            prefix+='<blockquote class="blockquote">'
        for i in range(curquote,quote):
            prefix+='</blockquote>'
        quote=curquote
        return prefix+parse_markdown(string,parent_quote=True)
    if not parent_quote and quote != 0:
        for i in range(0,quote):
            prefix+="</blockquote>"
        quote=0
    if (len(string)) == 0:
        return prefix+"<br>"
    if len(string) > 3 and (string[0] == "*" or string[0] == "-" or string[0] == "_")and string.count(string[0])==len(string):
        return prefix+"<hr>"
    if (string[-2:]=="  "):
        return prefix+parse_markdown(string[:-2],parent=True)+"<br>"
    if (string[0]=="#"):
        space=string.find(" ")
        c=string[0:space-1].count("#")
        if space==-1 or string[space+1:].count(" ")==len(string)-space-1:
            return "<br>"
        if (space-1==c):
            ID+=1
            c+=1
            temp="<h"+str(c)+'>'+parse_markdown(string[space+1:],parent=True)+"</h"+str(c)+">"
            headers.append((temp,str(ID)))
            temp=prefix+temp[:3]+' id="gheader'+str(ID)+'"'+temp[3:]
            return temp
    bold=False
    boldamount=string.count("**")//2*2
    ba=0
    italic=False
    ia=0
    italicamount=string.count("__")//2*2
    code=False
    link=False
    link2=False
    codeamount=string.count("`")//2*2
    ca=0
    startindex=0
    tags=[]
    currentstring=""
    index=-1
    while index in range(-1,len(string)-1):
        index+=1
        appendtag=False
        c=string[index]
        if c == "`":
            if ca < codeamount:
                code=not code
                ca=ca+1
                if not code: # We have just closed a code fragment
                    tags.append((string[startindex+1:index],"code"))
                    continue
                else: # A new one starts : SAVE INDEX + SAVE CURRENT STRING !
                    appendtag=True
        elif not code:
            if c == "*" and len(string) > index+1 and string[index+1] == "*" and ba < boldamount and not italic:
                index+=1
                bold=not bold
                ba=ba+1
                if not bold: # We have just closed a code fragment
                    tags.append((string[startindex+1:index-1],"bold"))
                    continue
                else: # A new one starts : SAVE INDEX + SAVE CURRENT STRING !
                    appendtag=True
            elif c == "_" and len(string) > index+1 and string[index+1] == "_" and ia < italicamount and not bold:
                index+=1
                italic=not italic
                ia=ia+1
                if not italic: # We have just closed a code fragment
                    tags.append((string[startindex+1:index-1],"italic"))
                    continue
                else: # A new one starts : SAVE INDEX + SAVE CURRENT STRING !
                    appendtag=True
            elif c == "<" and not link:
                appendtag=True
                link=True
            elif c == ">" and link:
                link=False
                tags.append((string[startindex+1:index],"link"))
                continue
            elif c == "!" and len(string) > index+1 and string[index+1] == "[":
                breakit=False
                text=""
                index+=1
                for i in range(index+2,len(string)-3):
                    c2=string[i]
                    if (c2 == "]"):
                        text=string[index+1:i]
                        if string[i+1]=="(":
                            for j in range(i+3,len(string)):
                                c3=string[j]
                                if (c3 == ")"):
                                    breakit=True
                                    imglink=string[i+2:j].split(" ",1)
                                    tags.append((img(text,imglink[0],imglink[1]),"image"))
                                    index=j+1
                        break
                if breakit:
                    continue
            elif c == "[":
                breakit=False
                text=""
                for i in range(index+2,len(string)-3):
                    c2=string[i]
                    if (c2 == "]"):
                        text=string[index+1:i]
                        if string[i+1]=="(":
                            for j in range(i+3,len(string)):
                                c3=string[j]
                                if (c3 == ")"):
                                    breakit=True
                                    tags.append((text,"link",string[i+2:j]))
                                    index=j+1
                        break
                if breakit:
                    continue
        if appendtag:
            tags.append((currentstring,"normal"))
            currentstring=""
            startindex=index
            continue
        if not bold and not italic and not code and not link and not link2:
            currentstring+=c
    if len(currentstring)  != 0:
        tags.append((currentstring,"normal"))
    result=""
    for tag in tags:
        string=tag[0]
        p=""
        s=""
        wrap=False
        if tag[1]=="code":
            p,s="<code>","</code>"
        elif tag[1]=="bold":
            p,s="<b>","</b>"
            wrap=True
        elif tag[1]=="italic":
            p,s="<em>","</em>"
            wrap=True
        elif tag[1]=="link":
            if len(tag) == 2:
                if tag[0][0:4] == "http": # CHECK LINKS !
                    p,s='<a href="'+tag[0]+'">',"</a>"
            else:
                p,s='<a href="'+tag[2]+'">',"</a>"
        elif tag[1]=="image":
            result+=tag[0]
            continue
        elif tag[1]=="italic":
            p,s="<em>","</em>"
        if wrap:
            result+=p+parse_markdown(string,parent_quote=True,parent=True)+s
        else:
            result+=p+html_escape(string)+s
    if parent_quote and parent:
        return result
    return prefix+"<p>"+result+"</p>"

def parse_md(string): # Parse line by line
    lines=string.split("\n")
    ret=""
    for i in range(len(lines)-1,0,-1): # Convert alternate header writings(underlines)
        if abs(len(lines[i-1])-len(lines[i])) < 3  and len(lines[i]) > 0:
            if lines[i].count("=")==len(lines[i]):
                lines[i]=""
                lines[i-1]="# "+lines[i-1]
            elif lines[i].count("-")==len(lines[i]):
                lines[i]=""
                lines[i-1]="## "+lines[i-1]
    i=0
    ident=False
    segments=0
    for line in lines:
        prefix=""
        suffix=""
        asteriskpos=line.find("*")
        # or (len(line) > 1 and line[0]=="\t" and (asteriskpos==-1 or line[0:asteriskpos].count("\t") != asteriskpos)))
        if liste== 0 and ((len(line) > 4 and line[0:4]==" "*4 and (asteriskpos==-1 or asteriskpos > 1 or line[0:asteriskpos].count(" ") != asteriskpos))):
            if not ident:
                prefix="<pre><code>"
                #print("START : "+line[4:])
                ident=True
        elif ident:
            ident=False
            prefix="</code></pre>"
            segments+=1
        #else:
            #if (len(line > 4)
            #print("{"+line[0:4]+";"+line[0]+"}")
            
        lval=""
        if ident:
            lval=html_escape(line[4:])+"\n"
        else:
            lval=parse_markdown(line)
        ret+=prefix+lval
        i=i+1
    print("**Found "+str(segments)+" multi-line code segments.**")
    if ident:
        ident=False
        return ret+"</code></pre>"
    return ret

def code(): # Parse multi-line code fragments
    global markdown
    last=-1
    i=0
    stuff=[]
    while (i < len(markdown)):
        if markdown[i:i+3]=="`"*3: # Handle GitHub style code tags
            i=i+3
            if last < 0:
                start=-(last+1)
                last=i
                stuff.append((markdown[start:last-3],False))
            else:
                stuff.append((markdown[last:i-3],True))
                last=-i-1
        i=i+1

    start=-(last+1)
    stuff.append((markdown[start:],False))
    #print(stuff)

    markdown=""
    for s in stuff:
        if s[1]:
            markdown+="<pre><code>"+s[0]+"</code></pre>"
        else:
            markdown+=parse_md(s[0])

# This python script grabs the newest lua_api.txt from Minetest GitHub repo and converts it to HTML, plus adding some bookmarks & css
# So mainly MD -> HTML. Written by me to improve my rusty Python skills.
# © Lars Müller @appguru.eu

directory=input("Directory name : ")
html_files={}
for a,b,files in walk(directory):
    for file in files:
        final = open(join(directory,file), 'r').read()
        content=final.split("\n",1)
        head=content[0].split(":",1)

        print("**Converting "+file+"...**")

        #markdown = parse.unquote(content[1]) # Read & convert
        markdown=content[1]
        liste=0 # Which sublist we are in right NOW
        quote=0 # Which blockquote we are in right NOW
        headers=[] # Stores all the headers + IDs
        ID=0 # Stores header ID counter

        print("**Starting parsing...**")

        code()

        print("**...finished parsing.**")

        nav=""

        print("**Creating content table...**")

        for header in headers:
            nav+="""<li><a class="nav-link" href="#gheader"""+header[1]+"""">"""+header[0]+"""</a></li>""" # Create navbar

        print("**...finished creating content table. "+str(len(headers))+" Headers are included.**")

        html_files[splitext(file)[0]]=(head[0],head[1],markdown,nav)

print("**Reading template...**")
template = open('template.html', 'r').read()
from os import mkdir
try:
    mkdir(directory+"_page")
except:
    print("**Directory already exists.**")

for key,val in html_files.items():
    print("**Inserting "+key+" into template file...**")
    string=template.replace("<!--PLACETITLE-->",val[0])
    string=string.replace("<!--PLACESTUFF-->",val[2])
    string=string.replace("<!--PLACENAV-->",val[3])
    navi='<a class="nav-link" href="index.html">Home</a>'
    for key2,val2 in html_files.items():
        if key != key2:
            navi+='<a class="nav-link" href="'+key2+'.html">'+val2[0]+'</a>' # Create navbar
        else:
            navi+='<a class="nav-link active" id="v-pills-home-tab" data-toggle="pill" href="'+key2+'.html" role="tab" aria-controls="v-pills-home" aria-selected="true">'+val2[0]+'</a>'
    string=string.replace("<!--PLACENAV2-->",navi)
    file = open(join(directory+"_page",key+'.html'), 'w') # SAVE AS lua_api.html
    file.write(string)
    print("**...saved.**")
    file.close()

preview=""  
for key2,val2 in html_files.items():
        preview+='<div class="col-sm"><h2><a href="'+key2+'.html">'+val2[0]+""" &raquo;</a></h2>
                        <p>"""+val2[1]+"""
                        </p>
                    </div>"""

print("**Reading preview template...**")
template = open('index_template.html', 'r').read()
string=template.replace("<!--PLACESTUFF-->",preview)
file = open(join(directory+"_page",'index.html'), 'w') # SAVE
file.write(string)
print("**Preview saved.**")
file.close()

from shutil import copyfile,rmtree

try:
    copyfile("jumbotron.css",join(directory+"_page","jumbotron.css"))
except:
    rmtree(join(directory+"_page","jumbotron.css"))
    copyfile("jumbotron.css",join(directory+"_page","jumbotron.css"))
    print("**Stylesheets already exist.**")
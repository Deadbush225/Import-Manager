import pypandoc

with open(r"C:\Users\Eliaz\Desktop\Fatima Admission Requirements.docx", "r", encoding="latin-1") as word:
    r = word.read()
    # print(r.encode())

    output = pypandoc.convert_text(r, 'docx', format='html', outputfile=r"C:\Users\Eliaz\Desktop\Req.html")
    
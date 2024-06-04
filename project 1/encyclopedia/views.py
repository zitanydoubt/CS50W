from django.shortcuts import render, redirect
import markdown2 as md
from django import forms
from django.contrib import messages
import random
from . import util

class EntryForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Title of the Entry"}), label = "Title")
    content = forms.CharField(widget = forms.Textarea(attrs={"placeholder": "Describe the Entry here ..."}), label = "Content")


def index(request):
    """
    renders index page with list of all encyclopedia entries
    """
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    """
    displays entry if there is one 
    """
    entry_content = util.get_entry(entry)
    if entry_content is not None:
        entry_html = md.markdown(entry_content)
    else: 
        entry_html = None
    return render(request, "encyclopedia/entry.html", {
            "entry": entry_html,
            "title": entry
    })
      
def search(request):
    """ 
    search function which redirects to the page of the searched for entry
    or provides a list of similar entries 
    """
    query = request.GET.get("q").lower().strip()
    entries = util.list_entries()
    if query in [entry.lower() for entry in entries]:
        return redirect("entry", entry=query)
    else:
        return render(request, "encyclopedia/search.html", {
            "entries": [entry for entry in entries if query in entry.lower()]
        })
    
def new(request):
    """ 
    Lets user create new wiki encyclopedia entry 
    """
    if request.method == "POST":
        form = EntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"].strip()
            content = form.cleaned_data["content"]
            entries = util.list_entries()
            if title.lower().strip() in [entry.lower() for entry in entries]:
                messages.error(request, "This entry already exists.")
            else:
                util.save_entry(title, f"# {title}\n\n{content}")
                return redirect("entry", entry=title)
    return render(request, "encyclopedia/new.html", {
        "form": EntryForm()
    })


def edit(request, entry):
    """
    Lets user edit a wiki encyclopedia entry
    """
    content_initial = util.get_entry(entry).split("\n\n", maxsplit=1)[1]
    if request.method == "POST":
        form = EntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"].strip()
            content_edited = form.cleaned_data["content"]
            util.save_entry(title, f"# {title}\n\n{content_edited}")
            return redirect("entry", entry=title)
    return render(request, "encyclopedia/edit.html", {
        "title": entry,
        "form": EntryForm(initial={"title": entry, "content": content_initial})
    })

def random_entries(request):
    """ 
    Lets user view random wiki encyclopedia entry
    """
    random_entry = random.choice(util.list_entries())
    return redirect("entry", entry=random_entry)
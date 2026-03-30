SHELL := /bin/bash
GIT_ROOT := $(shell git rev-parse --show-toplevel 2>/dev/null)
ETC := $(GIT_ROOT)/etc
RUN_TEST := bash $(ETC)/run_tests.sh

CLS    := '\033[H\033[J'
cRESET := '\033[0m'
cYELLOW:= '\033[1;33m'

help: ## show help
	@gawk -f $(ETC)/help.awk $(MAKEFILE_LIST) 

push2pypi: ## push to PyPi
	pip install build twine
	python3 -B -m build
	twine upload dist/*
	rm -rf dist build *.egg-info

pyclean: ## remove python temporaries
	cd $(GIT_ROOT); find . -type d -name __pycache__ -exec rm -rf {} +
	cd $(GIT_ROOT); find . -type d -name .pytest_cache -exec rm -rf {} +
	cd $(GIT_ROOT); find . -type d -name "*.egg-info" -exec rm -rf {} +

sh: ## demo of my shell
	@-echo -e $(CLS)$(cYELLOW); figlet -W -f slant peEK.ai; echo -e $(cRESET)
	@-bash --init-file $(ETC)/bash.rc -i

push: ## save to cloud
	@read -p "Reason? " msg; git commit -am "$$msg"; git push; git status

CSVS=ls -r ~/gits/moot/optimize/*/*.csv | xargs -P 32 -I {} sh -c 

~/tmp/peeksrun.log :
	@$(CSVS) 'python3 -B peeks.py --run {} 2>&1' | tee $@
	cut -d \  -f 1 $@ | sort -n | fmt -17 #65

~/tmp/peeksguess.log :
	@$(CSVS) 'python3 -B peeks.py --guess {} 2>&1' | tee $@
	cut -d \  -f 1 $@ | sort -n | fmt -65

~/tmp/%.pdf: %.py $(MAKEFILE_LIST) ## .py ==> .pdf
	@mkdir -p ~/tmp
	@echo "pdf-ing $@ ... "
	@a2ps -Br --quiet --landscape --chars-per-line=90 --line-numbers=1  \
	          --borders=no --pro=color --columns=3 -M letter -o - $< \
						| ps2pdf - $@
	@open $@

# K=1
#
# -345381173658630070302088494055424 1 8 15 16 27 33 35 35 42 42 43
#  44 44 45 45 46 46 47 47 47 48 50 50 50 50 50 51 51 52 52 53 53 54
#  55 56 56 56 56 59 59 59 59 60 60 61 61 63 64 64 67 68 69 70 71 71
#  72 74 74 76 76 76 76 76 77 78 78 78 79 79 80 81 81 81 82 82 82 83
#  83 84 84 85 87 87 87 88 88 88 88 89 89 89 90 91 92 92 92 93 93 93
#  93 93 94 94 94 94 95 95 95 95 95 95 96 96 96 96 96 97 97 97 97 97
# K=K
Html := $(GIT_ROOT)/docs

docs: $(Html)/peek.html $(Html)/peek.pdf

$(Html)/%.html: %.py
	@mkdir -p $(Html)
	@awk "$$AWK_PY" $< > $(Html)/$<
	@cd $(Html) && pycco -d . $<
	@echo "$$CUSTOM_CSS" >> $(Html)/pycco.css
	@awk "$$AWK_HTML" $@ > $@.tmp && mv $@.tmp $@
	@rm $(Html)/$<

# Pre-processor for Python -> Markdown headers
define AWK_PY
/^#[ \t]*[-—]{4}/ {
  sub(/^#[ \t]*[-—]+[ \t]*/, ""); sub(/[ \t]*[-—]+.*$$/, "");
  print "# ## " $$0 "\n\n"; next
}
/^#[ \t]*[-—]{3}/ {
  sub(/^#[ \t]*[-—]+[ \t]*/, ""); sub(/[ \t]*[-—]+.*$$/, "");
  print "# ### " $$0 "\n\n"; next
}
/^#[ \t]*[-—]{2}/ {
  sub(/^#[ \t]*[-—]+[ \t]*/, ""); sub(/[ \t]*[-—]+.*$$/, "");
  print "# #### " $$0 "\n\n"; next
}
/^[ \t]*(def|class)/ { h=$$0; next }
h && /"""/           { gsub(/"""/,""); print "#"$$0; print h; h=""; next }
h                    { print h; h="" }
1
endef
export AWK_PY

# Post-processor for Pycco HTML
define AWK_HTML
BEGIN { s=0 }
/<body/ {
  print; print ENVIRON["HEADER_HTML"]; next
}
/<h2>/ { s=1 }
/class=.section/ {
  if(!s) sub(/class=\047section\047/, "class=\047section intro\047")
}
1
endef
export AWK_HTML

define HEADER_HTML
<link rel="stylesheet"
  href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<div class="custom-header" style="background:#f8f9fa; padding:12px 30px;
  border-bottom:1px solid #ddd; font-family:Optima, Candara, sans-serif;
  display: flex; justify-content: space-between; align-items: center;
  overflow-x: auto; white-space: nowrap;">
  <div style="font-size: 1.05em; font-weight: 500; display: flex; gap: 20px;
    flex-shrink: 0; white-space: nowrap;">
    <a href="https://github.com/timm/PROJECT" target="_blank"
      style="text-decoration:none; color:#0366d6; display: flex;
      align-items: center; gap: 5px;">
      <i class="fa-brands fa-github"></i> GitHub
      <i class="fa-solid fa-arrow-up-right-from-square"
        style="font-size:0.7em;"></i>
    </a>
    <a href="https://github.com/timm/PROJECT/issues" target="_blank"
      style="text-decoration:none; color:#0366d6; display: flex;
      align-items: center; gap: 5px;">
      <i class="fa-solid fa-circle-exclamation"></i> Issues
      <i class="fa-solid fa-arrow-up-right-from-square"
        style="font-size:0.7em;"></i>
    </a>
  </div>
  <div style="display: flex; gap: 10px; align-items: center; flex-shrink: 0;
    margin-left: 20px;">
    <img style="height:22px;" alt="Python"
      src="https://img.shields.io/badge/python-3.12+-3776ab.svg?style=flat-square&logo=python&logoColor=white">
    <img style="height:22px;" alt="XAI"
      src="https://img.shields.io/badge/topic-XAI-purple.svg?style=flat-square">
    <a href="https://opensource.org/licenses/MIT" target="_blank"
      style="display:flex; align-items:center;">
      <img style="height:22px; border:none;" alt="MIT"
        src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square">
    </a>
  </div>
</div>
endef
export HEADER_HTML

define CUSTOM_CSS
/* 1. Fonts and Basic Styling */
body, div.docs, p { 
  font-family: Optima, Candara, "Noto Sans", sans-serif !important; 
  font-size: 15px; color: #333; 
}
pre, code, .code { font-family: "JetBrains Mono", "Fira Code", monospace; }

/* 2. GAP KILLER: Remove Pycco's default top padding/margins */
#container { margin-top: 0 !important; }
div.docs, div.code { padding-top: 10px !important; }

/* 3. The "Hugging" Text */
div.docs, div.docs p {
  text-align: right !important; padding-right: 35px !important;
}

/* 4. Left-Anchored Headers */
div.docs h1, div.docs h2, div.docs h3 { 
  text-align: left !important; border-bottom: 1px solid #eee; 
  width: 100%; display: block; margin-top: 40px; 
}

/* 5. Special case: First H1 should have almost no top margin */
div.docs h1:first-child, div.section:first-child h1 { 
  margin-top: 5px !important; 
}
div.docs h3 { border-bottom: none; color: #555; }

/* 6. LHS Code Blocks */
div.docs pre {
  text-align: left !important; margin: 20px 0 !important;
  font-size: 0.75em !important; background: #fdfdfd; padding: 15px;
  border: 1px solid #eee; border-left: 4px solid #7D9029;
}
div.section.intro div.docs, div.section.intro div.docs p {
  text-align: left !important;
}
endef
export CUSTOM_CSS


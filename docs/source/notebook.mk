PYTHON ?= $(shell which python)
JUPYTER ?= $(shell which jupyter)
NBCONVERT ?= ${JUPYTER} nbconvert
PS     ?= $(shell ${PYTHON} -c "import os; print(os.pathsep)")

SOURCE  ?= .
IPYNBS  := $(shell find ${SOURCE} -name *.ipynb -not -name *.result.ipynb)
RESULTS := $(addsuffix .result.ipynb, $(basename ${IPYNBS}))

%.result.ipynb: %.ipynb
	cp "$(shell readlink -f $<)" "$(shell readlink -f $@)" && \
		cd "$(shell dirname $(shell readlink -f $<))" && \
		PYTHONPATH="$(shell dirname $(shell readlink -f $<))${PS}${PYTHONPATH}" \
		$(NBCONVERT) --to notebook --inplace --execute "$(shell readlink -f $@)"

build: ${RESULTS}

all: build

clean:
	rm -rf \
		$(shell find ${SOURCE} -name *.result.ipynb)
	for nb in ${IPYNBS}; do \
		if [ -f $$nb ]; then \
			$(NBCONVERT) --clear-output --inplace $$nb; \
		fi; \
	done;

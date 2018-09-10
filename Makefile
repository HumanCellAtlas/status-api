.PHONY: secrets
secrets:
	aws secretsmanager get-secret-value \
		--secret-id status-api/_/config.json | \
		jq -r .SecretString | \
		python -m json.tool > terraform.tfvars

default: build

.PHONY: clean
clean:
	@rm -rf target lambda.zip

.PHONY: target
target:
	@mkdir -p target

.PHONY: init
init:
	terraform init \
		-backend-config bucket=$(shell jq -r .terraform_bucket terraform.tfvars) \
		-backend-config region=$(shell jq -r .aws_region terraform.tfvars) \
		-backend-config profile=$(AWS_PROFILE)

.PHONY: install
install:
	virtualenv -p python3 venv
	. venv/bin/activate && pip install -r requirements.txt --upgrade

.PHONY: test
test:
	. venv/bin/activate && python -m unittest discover -s tests -p '*_tests.py'

.PHONY: build
build: clean target
	@venv/bin/pip install -r requirements.txt -t target/ --upgrade > /dev/null
	@cp *.py target/
	@cd target && zip -r ../lambda.zip * > /dev/null
	@echo '{"status": "done"}'

.PHONY: deploy
deploy:
	terraform apply \
		-var aws_profile=$(AWS_PROFILE) \
		-var-file terraform.tfvars

.PHONY: all
all:
	make install && make secrets && make build && make deploy && make test

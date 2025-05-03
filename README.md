# Anime Data Pipeline

A simple anime data pipeline to try out some data engineering and devops tech.

- Uses [Dagster](https://dagster.io/) to create a job to download data from the [AniList API](https://docs.anilist.co/) for a given user
- Uses [Pandas](https://pandas.pydata.org/) and [dbt-core](https://github.com/dbt-labs/dbt-core) to transform the data into fact and dimension tables, then store the data in [DuckDB](https://duckdb.org)
- Uses [Terraform](https://developer.hashicorp.com/terraform) and [minikube](https://minikube.sigs.k8s.io/docs/) to deploy a local [Kubernetes](https://kubernetes.io/) cluster to run the Dagster dev server
- Uses [Github actions](https://docs.github.com/en/actions) to automatically run tests on push

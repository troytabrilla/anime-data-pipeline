# Anime Data Pipeline

A simple anime data pipeline to try out some data engineering and devops tech.

- Uses [Dagster](https://dagster.io/) to create a job to download data from the [AniList API](https://docs.anilist.co/) for a given user, transform the data into fact and dimension tables, then store the data in [DuckDB](https://duckdb.org)
- Uses [Terraform](https://developer.hashicorp.com/terraform) and [minikube](https://minikube.sigs.k8s.io/docs/) to deploy a local [Kubernetes](https://kubernetes.io/) cluster to run the Dagster dev server
- Uses a [Github action](https://docs.github.com/en/actions) to automatically run tests on push

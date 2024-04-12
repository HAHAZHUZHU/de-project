

# 优质课程笔记

https://github.com/boisalai/de-zoomcamp-2023/blob/main/week2.md 



# week_1_basics_n_setup

## 1_treeaform_gcp

每次在终端启动 docker 镜像，尽管上一次在这个镜像 pip install 了一些包，下次再启动这个镜像，也是没有上次安装好的东西的。所以，如果想要每次启动这个镜像的时候，都安装好了我们想要的包，那就把需要安装的包写在 Dockerfile 文件中。



## 2_docker_sql

### 1. Introduction to Docker

**一些需要注意的点：**

Running Postgres Database image on our host machine:

```dockerfile
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v "$(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data" \
  -p 5432:5432 \
  postgres:13
```

**Notice：**-v 后面的命令要加双引号，这部分命令是将本地主机的一个目录映射到Docker容器中的一个目录，这样做的目的是为了持久化存储PostgreSQL数据库的数据，即使容器被删除或重新创建，数据也不会丢失。

具体来说，`$(pwd)/ny_taxi_postgres_data` 是本地主机中的一个目录路径，它通过 `$(pwd)` 获取当前工作目录的绝对路径，并在该路径下创建一个名为 `ny_taxi_postgres_data` 的目录。

然后，`-v "$(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data"` 这部分命令将本地主机的 `ny_taxi_postgres_data` 目录映射到了Docker容器中的 `/var/lib/postgresql/data` 目录。这样，容器中的 PostgreSQL 数据库就会将其数据存储在 `/var/lib/postgresql/data` 目录中，而该目录实际上是映射到了本地主机上的 `ny_taxi_postgres_data` 目录。

这种映射方式的好处是，即使容器被删除或重新创建，本地主机上的 `ny_taxi_postgres_data` 目录中的数据仍然会被保留，因此可以实现持久化存储。



### 从 Dockerfile 构建镜像

docker build -t test:pandas .

从当前文件夹中构建 image, 并在当前文件夹中寻找 Dockerfile 进行构建，image 的名字为：test:pandas，后面的 . 代表，将当前文件夹中的所有文件都构建进 image 中。



当我们建立了dockerfile 后，就可以通过 `docker build` 命令来创建 docker image，有了 docker image 我们才能创建出 docker instance，来运行我们的应用和服务。



### 新建并启动容器

启动容器有两种方式:

1. 一种是基于镜像新建一个容器并启动（需要的命令主要为 `docker run -it`）
2. 另外一个是将在终止状态（`exited`）的容器重新启动（需要的命令主要为 `docker restart [CONTAINER ID]` ）



### Docker 命令

我们可以通过如下命令，来查看我们运行中的容器实例列表和状态

```bash
docker ps -a
```

重启 Docker

```
sudo service docker restart
```



### 2. Ingesting NY Taxi Data to Postgres

在运行 下面这条命令的时候，会报错，提示 No module named 'psycopg2'

```
pip install sqlalchemy
```

**解决办法：**

```
pip install psycopg2
```



We run Postgres using docker, we run it locally and then we were able to connect to these database (using sqlalchemy), then we took a look at the data and then we started putting this data to our Postgres database.



### 3. Connecting pgAdmin and Postgres

拉取 pgAdmin 的 docker image, 运行成功以后，pgadmin 运行在 8080 端口，但是这时，不能直接 register new server, 因为, 这时候，我们要连接的 database 的 host name 为 localhost, 但是，pgadmin 是从 docker 运行的，此时的 localhost 指的是 pgadmin containner 本身，这个 containner 里面是没有 postgres database 的。我们的 postgres database 运行在另外一个 containner 中。

**解决方案：**

create network, put them in the same network.



### 4. Putting the ingestion script into Docker

-- docker build -t taxi_ingest:v001 .

URL="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"

or

URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"

```dockerfile
docker run -it \
  --network=pg-network \
  taxi_ingest:v001 \
      --user=root \
      --password=root \
      --host=pg-database \
      --port=5432 \
      --db=ny_taxi \
      --tb=yellow_taxi_trips \
      --url=${URL}
```

 

注意这两部分命令，我们首先根据 Dockerfile 构建了镜像，构建成功完成以后，开始 run 这个
镜像，其中，--network=pg-network 这一行命令是因为我们现在运行的是刚构建好的
镜像，但是这个镜像中并没有 postgres 数据库，所以，我们需要把当前这个镜像运行在 和 
Postgres 数据库镜像相同的 network 中，又因为，我们已经将 postgres 的镜像运行在了
pg-network 网络中，所以，我们只要把刚刚构建的镜像也指定他运行在这个网络中，那么，这个镜像
就可以连接数据库了。

除此之外，--host=pg-database，这一句命令，本来是 --host=localhost, 改成 pg-database
的原因是：我们现在是在镜像中运行我们的 python 脚本，镜像的 localhost 就是他自己（镜像），
而不是我们的 本地，所以，我们需要将其更改为 运行 postgres 镜像时候，给他指定的名字。

copy 到镜像中的 python 文件中的 curl 语句下载的文件，应该是在容器中，因为我们执行了 docker run，启动了镜像，从而运行了 python 文件，python 文件是从容器里运行的。但是下载的文件的位置找不到在哪里

目前为止，主要用到了以下 3 种镜像：
  -- postgres 的镜像：数据库
  -- pgadmin 的镜像：数据库的图形界面，更直观的查看数据库中的数据，表，而且可以进行 SQL 查询
  -- 我们自己构建的镜像，其中会运行 python 脚本：利用 连接 postgres 数据库后，就可以在在数据库里面新建表，插入数据等



### 5. Running Postgres and pgAdmin with Docker-Compose

**How to install GCloud and Always Works after Restart On Mac OS**:

https://stackoverflow.com/questions/31037279/gcloud-command-not-found-while-installing-google-cloud-sdk



### Workshop: Creating GCP Infrastructure with Terraform

Install Google Cloud: https://cloud.google.com/sdk/docs/install-sdk?hl=zh-cn. 

Notice: after unzip the .tar.gz file, we need to run `./google-cloud-sdk/install.sh` this command, and after run this command, we still need to run `source ~/.zshrc` to make it working



解释 main.tf 中的配置命令：

1. **Terraform版本和后端设置：**

   ```
   hclCopy code
   terraform {
     required_version = ">= 1.0"
     backend "local" {}  # 可以更改为 "gcs" (用于Google Cloud) 或 "s3" (用于AWS)，以保存tf-state文件在线
     required_providers {
       google = {
         source  = "hashicorp/google"
       }
     }
   }
   ```

   - `terraform`块用于指定Terraform的配置。
   - `required_version`定义了Terraform的最低版本要求。
   - `backend`块指定了Terraform状态文件的存储方式，目前设置为本地（"local"），但你可以选择将其更改为Google Cloud Storage（"gcs"）或Amazon S3（"s3"）等在线存储方式。
   - `required_providers`定义了所需的提供商，这里指定了Google Cloud的提供商。

2. **Google提供商设置：**

   ```
   hclCopy code
   provider "google" {
     project    = var.project
     region     = var.region
     // credentials = file(var.credentials)  # 如果你不想设置环境变量GOOGLE_APPLICATION_CREDENTIALS，可以使用这行代码来指定凭证文件
   }
   ```

   - `provider "google"`块用于配置Google Cloud提供商。
   - `project`和`region`变量被用来设置项目和地区。
   - 注释中的`credentials`行是可选的，如果你不想设置环境变量`GOOGLE_APPLICATION_CREDENTIALS`，你可以使用这行代码来指定凭证文件路径。

3. **Data Lake Bucket资源：**

   ```
   hclCopy code
   resource "google_storage_bucket" "data-lake-bucket" {
     name          = "${local.data_lake_bucket}_${var.project}"
     location      = var.region
     storage_class = var.storage_class
     uniform_bucket_level_access = true
     
     versioning {
       enabled     = true
     }
     
     lifecycle_rule {
       action {
         type = "Delete"
       }
       condition {
         age = 30  // 天
       }
     }
     
     force_destroy = true
   }
   ```

   - 这部分定义了一个Google Cloud存储桶资源，用于创建一个数据湖存储桶。
   - `name`设置了存储桶的名称，采用了一个特定的命名约定，以确保名称的唯一性。
   - `location`和`storage_class`分别设置了存储桶的位置和存储类别。
   - `versioning`部分启用了版本控制，允许存储桶保存不同版本的对象。
   - `lifecycle_rule`部分定义了一个生命周期规则，指定了对象在30天后自动删除。
   - `force_destroy`设置为`true`，以确保在销毁存储桶时强制删除其中的所有对象。

4. **DWH资源：**

   ```
   hclCopy code
   resource "google_bigquery_dataset" "dataset" {
     dataset_id = var.BQ_DATASET
     project    = var.project
     location   = var.region
   }
   ```

   - 这部分定义了一个Google BigQuery数据集资源，用于创建数据仓库数据集。
   - `dataset_id`设置了数据集的ID。
   - `project`和`location`变量用于设置项目和地区。

这是一个Terraform配置文件的示例，用于在Google Cloud上创建存储桶和BigQuery数据集。你可以根据自己的项目需求修改这些设置。如果你需要进一步的帮助或有特定的问题，请告诉我，我将尽力提供更多详细信息。



```bash
export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your/service-account-authkeys>.json"
```

这一步，如果路径里面有空格的话，就不能带双引号



**Terraform 基本命令：**

`terraform init`: get the provider

`terraform plan`: list what this .tf file is going to create

`terraform apply`: apply my terraform configuration and create or update the resources

`terraform destory`: destroy all resources we created



### Setting up the environment on cloud VM

- Generating SSH keys

- Creating a virtual machine on GCP

- Connecting to the VM with SSH

   (`ssh -i ~/.ssh/your_private_key username_for_generating_SSH_KEY@VM_instance_external_ip`)

- Installing Anaconda

- Installing Docker

- Creating SSH `config` file

- Accessing the remote machine with VS Code and SSH remote

- Installing docker-compose

- Installing pgcli

- Port-forwarding with VS code: connecting to pgAdmin and Jupyter from the local computer

  (we can connect the postgres database which run on the docker in the VM instance from our local machine)

- Installing Terraform
- Using `sftp` for putting the service account json credential file to the remote machine
- Shutting down and removing the instance





# Week_2_workflow_orchestration

## 3. Introduction to Prefect concepts

**Purpose:** pulling the Yellow Taxi data into a Postgres DB and then it's going to transform that script to be orchestrated by Prefect.

运行 

```bash
pip3 install -r requirements.txt
```

 后，直接运行 

```bash
perfect version
```

 会报错，还需要运行 

```bash
pip3 install --upgrade pydantic prefect
```

 才可以

**注意：**

1. python version <= 3.10, 检查有没有装 wget, 可以用 wget --version 检查，如果没装的话，运行命令 brew install wget 来安装
2. 因为 prefect 的版本问题，需要运行 `pip install --force-reinstall -v "pydantic==1.10.0"` 命令，才能在 prefect server start 以后得图形界面的 Block 处，找到 sqlAlchemy connector 的 block, 以及运行 python3 ingest_data_flow.py 才不会报错



## 4. ETL with GCP & Prefect

这一小节的**主要目的**是：Putting data to Google Cloud Storage

**整体流程：**

write_local(): 将从 web 上抓取下来的，清洗过的 csv 文件，写入本地，并且写入为 parquet 类型的文件

write_gcs()：将本地 parquet 文件上传到 GCS（Google Cloud Storage） 中

在运行 etl_web_to_gcs.py 之前，我们需要先完成以下几步：

1. **Create a Bucket**

   - Go to [Gougle Cloud Console](https://console.cloud.google.com/).

   - In the **dtc-dez** project, select **Cloud Storage**, and select **Buckets** to create a new Bucket.

2. **Create GCS Bucket**

   Inside Prefect UI page, select **Blocks** at the left menu, choose the block **GCS Bucket** and click **Add +** button. Complete the form with:

   - Block Name: zoom-gcs
   - Name of the bucket: your_bucket_name

3. **Save Credential**

   在创建 GCS Bucket Block 的时候，有一项是需要选择 GCP Credential, 目的是为了给这个 GCS Bucket Block 赋权，也就是使得这个 Block 有权限使用他要用的 Bucket

   Under **Gcp Credentials**, click on **Add +** button to create a **GCP Credentials** with these informations:

   - Block Name: zoom-gcp-creds

   还要填写可以访问这个 Bucket 的 service account 的信息，所以，紧接着，我们需要创建一个 service account. 这个 service account 可以访问我们的 Bucket。

4. **Create service account**

   On **Google Cloud Console**, select **IAM & Admin**, and **Service Accounts**. Then click on **+ CREATE SERVICE ACCOUNT** with these informations:

   - Service account details: zoom-de-service-account
   - Click on **CREATE AND CONTINUE** button.
   - Give the roles **BigQuery Admin** and **Storage Admin**.
   - Click on **CONTINUE** button.
   - Click on **DONE** button.

   **Add the new key to the service account**
   Then, add a key on it. Click on ADD KEY + button, select CREATE A NEW KEY, select JSON and click on CREATE button.

   Past the content of the public key into the form of **Gcp Credentials**

最后，就可以运行 python etl_web_to_gcs.py 将本地 parquet 类型的数据上传到 GCS Bucket 里了




## 5. From Google Cloud Storage to Big Query

**整体思路：**

将存在于 GCS 中的数据导入到 Big Query 里面

1. 首先需要在 GCP 里面 ADD DATA，数据来源就是 GCS Bucket 中的文件
2. Under **Destination** section, click on **CREATE NEW DATASET** with the field **Dataset ID** equal to **dezoomcamp**. Under **Location type** section, select **Region** radiobox and set the field **REGION** to your region. Then click on **CREATE DATASET** button. Still under **Destination** section, name the table **rides**.
3. 代码里面，主要就是把之前创建好的 GCP Credential Block load 进来, 让我们的 Big Query 可以访问 GCS Bucket 中的文件

**代码中的注意点：**

`destination_table`：目标表的名称，通常以 `project_id.dataset_id.table_id` 的格式指定。

`chunksize` 值：你可以在数字中使用下划线，这只是为了提高数字的可读性，不会影响其值。所以 `chunksize=500_000` 和 `chunksize=500000` 是等价的，你可以根据自己的喜好选择其中一种方式来表示 `chunksize` 的值。



## 6. Parametrizing Flow & Deployments

https://medium.com/@dineshvarma.guduru/getting-started-with-prefect-task-orchestration-and-flows-prefect-cloud-565215878326 

看这个博客的 What is a deployment? 部分来理解，整个 deployment 的流程，怎么构建的，怎么 apply, apply 完以后，怎么 run 起来

https://github.com/boisalai/de-zoomcamp-2023/blob/main/week2.md （这个人的讲解，也可以看）



A run is an instance of our flow. Actually everytime we ran the flow file that is a flow run here

**在 command line 中将 flow 部署的流程：**

etl_parent_flow 是我的 flow, 也就是，主要入口 flow

```bash
prefect deployment build 03_deployments/parameterized_flow.py:etl_parent_flow -n "Parameterized ETL"
```

```bash
prefect deployment apply etl_parent_flow-deployment.yaml
```

```bash
prefect deployment run etl-parent-flow/Parameterized\ ETL -p "months=[1,2]"
```

```bash
prefect agent start --work-queue "default"
```





## 7. Schedules & Docker Storage with Infrastructure

列出所有本地的镜像：

```bash
docker images
```



在当前文件路劲构建镜像（前提是：Dockerfile 要和当前路径是同一层级的），镜像的名字为 docker_image_name，镜像的 tag 是 docker_image_tag，. 表示：指定上下文目录为当前目录

**注意：**因为我们要将构建好的镜像 push 到 Docker Hub 中，所以，在 build 的时候，需要用 username/docker_image_name 这种格式来构建镜像的名字，其中，username 是 Docker Hub 的用户名

You need to add your user name with the images name before building the image

```bash
docker build -t username/docker_image_name:docker_image_tag .
```



Push docker image to my dockerhub:

```bash
docker login -u username
docker push username/docker_image_name:docker_image_tag
```



### 启动容器

以下命令使用 ubuntu 镜像启动一个容器，参数为以命令行模式进入该容器

```
docker run -it ubuntu /bin/bash
```

要退出终端，直接输入 **exit**:

```
root@ed09e4490c57:/# exit
```



这一部分有很多需要注意的点：

1. 因为我们是直接在 docker container 里面 run flow, 所以，在我们构建好镜像以后，一定要进入本地镜像里面 pip show 一下对版本比较敏感的包，需要确定 docker image 里面的包的版本 和 本地的包的版本是一致的，因为，我们先在本地部署，运行 flow, 没有问题的话，把 flow 部分的代码放到 镜像 里面，再在 docker container 里面 run flow 是不会有问题的。
2. 因为代码中用到了 GCS Bucket, 而 GCS Bucket 又用到了 GCP Credentials，但又因为，我们是在 docker container 里面 run flow，docker container 里面是找不到在 GCP Credentials Block 中设定的 Service Account File 的 （the JSON file cannot be found by Prefect inside the Docker container）。解决方法是：we can just edit our GCP Credentials block and paste the content of our Service Account File as a secret dictionary ("Service Account Info") in the block.

**整体流程（CLI）：**

**Step 1:** 

```
docker image build --no-cache -t liurzdocker/prefect:zoom .

docker login

docker image push liurzdocker/prefect:zoom
```



**Step 2:** 

we need to create a Docker infrastructure block. In this step, I created a block named "zoom" and set the values of "Image", "ImagePullPolicy" and "Auto Remove".



**Step 3:** 

```bash
# -ib docker-container/zoom 中的 zoom 是我们在 prefect UI 中创建的 Block 的 Docker Container Block 的 name, docker-container 的作用的是告诉 prefect 要在 docker container 中部署并且 run flow code

# Overview of infrastructure in Prefect （https://docs.prefect.io/latest/concepts/infrastructure/）:
# Prefect uses infrastructure to create the environment for a user's flow to execute. Infrastructure is attached to a deployment and is propagated to flow runs created for that deployment.
# Users may specify an infrastructure block when creating a deployment. This block will be used to specify infrastructure for flow runs created by the deployment at runtime.

# -ib: Pre-configure infrastructure settings as blocks and base your deployment infrastructure on those settings — by passing -ib or --infra-block and a block slug when building deployment files.

# -q prod: 这指定了队列为 "prod"，这是流的目标队列

# --apply: 这表示立即将部署应用

prefect deployment build flows/03_deployments/parameterized_flow.py:etl_parent_flow -n "docker-flow" -ib docker-container/zoom -q prod --apply
```

```bash
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

```bash
prefect agent start -q prod
```

```
prefect deployment run etl-parent-flow/docker-flow -p "months=[3]"
```



## homework

Q4:

Store flow code into the Github repository

Build the deployment from CLI:

```bash
#  -sb github/dezoom: 这指定了部署的目标为 "github/dezoom"，通常用于指定部署到某个特定的目标环境或系统。

# 其中，dezoom 是我们在 prefect UI 中构建的 Github Block name

# Overview of storage (https://docs.prefect.io/latest/concepts/storage/): 
# Storage lets you configure how flow code for deployments is persisted and retrieved by Prefect workers (or legacy agents). Anytime you build a block-based deployment, a storage block is used to upload the entire directory containing your workflow code (along with supporting files) to its configured location. 

# -sb github/dezoom, 其中，dezoom 是我们在 prefect UI 中创建的 Github Block 的 name

prefect deployment build flows/02_gcp/homework2_q4.py:etl_web_to_gcs -n "github deploy" -sb github/dezoom -o gh.yaml --apply
```

```bash
prefect agent start -q 'default'
```







## 2.2. Configuring Mage

we can install Mage and run it within the docker container by following the readme file.

其中, docker-compose.yaml 文件中，

```
    volumes:
      - .:/home/src/
```

这一部分代码是为了，将当前路径下的所有文件都挂载到 docker container 中 的/home/src/ 下，这样做可以确保文件持久化存储，即使容器被删除或重建，数据也不会丢失。

如果宿主机上的文件发生了更新，容器内的文件会自动更新。这是因为数据卷的挂载是双向的，容器内的文件与宿主机上的文件是实时同步的。

当容器内的文件被修改时，实际上是在宿主机上的数据卷中进行了修改。同样地，当宿主机上的文件被修改时，容器内的文件也会立即反映这些变化。

这种双向同步的机制确保了容器内外数据的一致性，使得数据在容器和宿主机之间可以自由地共享和更新。



.env 文件中保存了我们需要用到的环境变量



在前几步骤中，我们跟着 Readme 文件执行完 docker compose build, docker compose up 以后，git clone 下来的项目中，就会多出 mage_data 和 magic-zoomcamp 两个文件夹。

We just initialized a new mage repository. It will be present in your project under the name `magic-zoomcamp`. If you changed the varable `PROJECT_NAME` in the `.env` file, it will be named whatever you set it to.

然后，我们就可以访问，localhost:6789 来访问 刚刚新建并且初始化的 Mage project

需要注意的是，我们的项目文件夹 project_name 中有一个 io_config.yaml 文件，可以在里面定义我们的配置环境，称为 profile。



## 2.2.3 - ETL: API to Postgres

我们在 Mage 中执行完 ETL 之后，可以在终端通过 `pgcli -h localhost -p 5432 -u postgres -d postgres` 连接到我们的数据库，并且可以在 data exporter block 中，我们定义的，将数据导出到的新的 schema_name.table_name 中查到导出的数据。

实现 docker container 中运行的 postgres 文件持久化：在 docker-compose.yml 文件中的 service 下的 postgres 中加入下面的配置，就可以将 `./mageai_ny_taxi_data` 路径下的文件挂载到容器中的 `/var/lib/postgresql/data` 中，实现文件持久化。也就是说，当我们在 docker 中运行的 postgres 中新加的所有改变，都能永久储存在 `./mageai_ny_taxi_data`  路径中。就算停止 docker container 或者 删除了 docker container。等下一次再重新运行 postgres 的 docker 镜像时，之前做的修改都是存在的。

```
    volumes:

​      - ../mageai_ny_taxi_data:/var/lib/postgresql/data
```





### 如何在gcloud中添加多个GCP账号，并对其进行配置和切换？

```
登录现有的 GCP 账号
gcloud auth login

添加一个新的 GCP 账号
gcloud auth login <new-account-email>

查看可用账号列表
gcloud auth list

试用账号的 ID 进行切换
gcloud config set account <account-ID>

配置每个账号的默认项目
gcloud config set project <project-name>
```





## Deployment

#### Deploying Mage use Terraform and Google Cloud

#### 1. Permissions

Go to the IAM management dashboard, find the service account associated to the account you just logged into, and then add these roles to that service account (e.g. choose your account as the principal when adding new roles):

1. Artifact Registry Read
2. Artifact Registry Writer
3. Cloud Run Developer
4. Cloud SQL
5. Service Account Token Creator



#### 2. Log into GCP from CLI

```
gcloud auth login
```



#### 3. Customize Terraform settings

**Project ID (REQUIRED)**

Before running any Terraform commands, please change the `default` value of the variable named `project_id` in the [./gcp/variables.tf](https://github.com/mage-ai/mage-ai-terraform-templates/blob/master/gcp/variables.tf) file.

```
variable "project_id" {
  type        = string
  description = "The name of the project"
  default     = "unique-gcp-project-id"
}
```

......

https://docs.mage.ai/production/deploying-to-cloud/gcp/setup

跟着这个 Mage 官方教程来，其中，**Secrets** 的这一部分，我们利用 Google Secret Manager 来创建一个 Secret，将我们的 service account credential json 文件存储进去。

**Google Secret Manager 基本介绍：**

通过 Google Secret Manager，您可以将敏感数据存储在云中，而不必担心泄露或意外访问。它提供了以下主要功能：

1. **安全存储**: Secret Manager 将您的敏感数据加密存储在 Google Cloud Platform 上，确保数据在传输和存储过程中的安全性。
2. **权限管理**: 您可以使用 Google Cloud IAM 权限控制机制来管理谁能够访问、修改或删除您的秘密数据。



创建完 Secret 以后，我们需要将这个 Secret 挂载到 the running Mage Cloud Run service（我们创建了一个 cloud run 服务，在这个服务中运行的是 Mage 的镜像。），需要做的是：

1. 在这个 cloud run 中定义 volumes, 将我们创建的 secert 赋值进去

2. 在这个 Mage docker container 中定义 volume_mount，也就是，要将这个 volume mount 到 Mage container 的哪里

3. 
   在 Terraform 的容器配置中，`mount_path` 和 `path` 是两个不同的字段，它们分别用于不同的目的。

   1. `mount_path`: 这个字段用于指定容器中挂载卷的目标路径。在容器运行时，指定的卷将会被挂载到容器中的 `mount_path` 所指定的路径下。换句话说，`mount_path` 是容器中卷的挂载点。
   2. `path`: 这个字段通常用于指定秘钥或其他资源在容器内部的路径。在您的示例中，`path` 字段指定了秘钥在容器内部的路径，以便容器中的应用程序可以访问秘钥的值。换句话说，`path` 是容器内部资源的路径。

   因此，`mount_path` 是用于容器卷的挂载点，而 `path` 是用于容器内部资源（如秘钥）的路径。这两个字段在容器配置中具有不同的作用，但通常用于实现容器中资源的访问和使用。



By default, the service account used by Cloud Run that needs access to the secret is the `Compute Engine` default service account. If you want to grant access to a different service account, configure the `service_account_name` argument in the `spec` block in [`main.tf`](https://github.com/mage-ai/mage-ai-terraform-templates/blob/master/gcp/main.tf#L99):

```
service_account_name = "[your service account email here]"
```



**注意：**secret 这部分，我们也可以不弄，可以通过在 variables.tf 中定义一个 credentials 变量，里面存储 sevice account credential json file path，然后，再在 main.tf 中 refer 这个变量就可以，但是这样的话，我们的 credential json file 需要存在于文件系统中，但是，如果通过设置 secret 的方式，我们是将 credential file 托管给 google cloud 的。



接着，运行下面的代码来 通过 terraform 将 Mage 部署到 Google cloud platform 上

```
cd gcp
terraform init
terraform plan
terraform apply
```



## Workshop1

### 如何理解Python中的yield用法?

https://zhuanlan.zhihu.com/p/268605982



### Hive分区表详细介绍

https://juejin.cn/post/7040689938521653285







## Module 3 Data Warehouse and BigQuery 

### 1. Data Warehouse

`INFORMATION_SCHEMA.PARTITIONS` 是 BigQuery 自带的信息模式，用于查询表的分区信息。这个系统视图提供了有关表分区的元数据，包括分区 ID、分区键值、分区位置和分区中的行数等信息。通过查询 `INFORMATION_SCHEMA.PARTITIONS`，可以方便地了解表的分区情况，以及每个分区中的数据量等信息



### 3. BigQuery Best Practices

**Denormalizing data**: 这里所说的数据去规范化指的是将原本分散在多个表中的数据合并到一个表中，从而减少在查询时需要进行的 JOIN 操作的次数和复杂度。通常情况下，数据规范化是指将数据按照一定的规则和范式分解到多个表中，以便降低数据冗余和提高数据的一致性。而数据去规范化则是相反的过程，即将原本分散的数据重新合并到一个表中，以简化查询操作并提高查询性能。


















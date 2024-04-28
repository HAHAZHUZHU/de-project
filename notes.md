

# 优质课程笔记

https://github.com/boisalai/de-zoomcamp-2023/blob/main/week2.md 



# week_1_basics_n_setup

## 1_treeaform_gcp

每次在终端启动 docker 镜像，尽管上一次在这个镜像 pip install 了一些包，下次再启动这个镜像，也是没有上次安装好的东西的。所以，如果想要每次启动这个镜像的时候，都安装好了我们想要的包，那就把需要安装的包写在 Dockerfile 文件中。



## 2_docker_sql

### Installing Google Cloud SDK

https://stackoverflow.com/questions/31037279/gcloud-command-not-found-while-installing-google-cloud-sdk



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





# Workshop: Creating GCP Infrastructure with Terraform

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





# Week_2_workflow_orchestration_2023



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





# Module 2 Workflow Orchestration 2024



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



# Workshop 1 (DLT)

## 如何理解Python中的yield用法?

https://zhuanlan.zhihu.com/p/268605982



## Hive分区表详细介绍

https://juejin.cn/post/7040689938521653285



## Introduction of DLT:

dlt is a python library created for the purpose of assisting data engineers to build simpler, faster and more robust pipelines with minimal effort.

You can think of dlt as a loading tool that implements the best practices of data pipelines enabling you to just “use” those best practices in your own pipelines, in a declarative way.

This enables you to stop reinventing the flat tyre, and leverage dlt to build pipelines much faster than if you did everything from scratch.

dlt automates much of the tedious work a data engineer would do, and does it in a way that is robust. dlt can handle things like:

- Schema: Inferring and evolving schema, alerting changes, using schemas as data contracts.
- Typing data, flattening structures, renaming columns to fit database standards. In our example we will pass the “data” you can see above and see it normalised.
- Processing a stream of events/rows without filling memory. This includes extraction from generators.
- Loading to a variety of dbs or file formats.

https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2024/workshops/dlt_resources/data_ingestion_workshop.md



## Load to bigquery

官方教程：https://dlthub.com/docs/dlt-ecosystem/destinations/bigquery

用教程里的方法一就行，把 secrets.toml 中的内容进行替换，替换成自己的 service account credential json 的内容

跟着做就行，但是要提前在 Bigquery 上创建好一个空的 dataset







# Module 3 Data Warehouse and BigQuery 

## 1. Data Warehouse

`INFORMATION_SCHEMA.PARTITIONS` 是 BigQuery 自带的信息模式，用于查询表的分区信息。这个系统视图提供了有关表分区的元数据，包括分区 ID、分区键值、分区位置和分区中的行数等信息。通过查询 `INFORMATION_SCHEMA.PARTITIONS`，可以方便地了解表的分区情况，以及每个分区中的数据量等信息



## 3. BigQuery Best Practices

**Denormalizing data**: 这里所说的数据去规范化指的是将原本分散在多个表中的数据合并到一个表中，从而减少在查询时需要进行的 JOIN 操作的次数和复杂度。通常情况下，数据规范化是指将数据按照一定的规则和范式分解到多个表中，以便降低数据冗余和提高数据的一致性。而数据去规范化则是相反的过程，即将原本分散的数据重新合并到一个表中，以简化查询操作并提高查询性能。





# Module 4 Analytics Engineering

## Notes worth referring to

https://github.com/ziritrion/dataeng-zoomcamp/blob/main/notes/4_analytics.md

https://github.com/Balajirvp/DE-Zoomcamp/blob/main/Week%204/Data%20Engineering%20Zoomcamp%20Week%204.ipynb

https://medium.com/@oktavianidewi/de-zoomcamp-2023-learning-week-4-analytics-engineering-with-dbt-53f781803d3e



## The difference of fact table and dimension table

事实表（Fact Table）和维度表（Dimension Table）是数据仓库中常见的两种表，它们之间有以下区别：

1. **数据内容**：
   - **事实表**包含了业务过程中的事实（例如销售数量、收入金额等）以及与这些事实相关的外键，用于描述业务过程中发生的事件或行为。
   - **维度表**包含了与事实表中的事实相关的维度信息，如日期、地理位置、产品类型等，用于对事实进行描述和分析。
2. **粒度**：
   - **事实表**通常以较低的粒度存储数据，即每一行记录代表了一个具体的业务事实。
   - **维度表**通常以较高的粒度存储数据，即每一行记录代表了一个维度的属性。
3. **大小**：
   - **事实表**通常比较大，因为它存储了大量的事实数据。
   - **维度表**通常比较小，因为它存储了维度属性的描述信息，而维度属性通常是有限且不会频繁变化的。
4. **用途**：
   - **事实表**用于记录业务过程中发生的事实事件，并支持基于事实数据的分析和报告。
   - **维度表**用于描述和分析事实数据的上下文信息，如时间、地点、产品等的属性。

举例说明： 假设我们有一个零售业务的数据仓库，其中包含销售数据。以下是一个简化的示例：

- **事实表**：销售事实表包含了每一笔销售交易的具体信息，如销售日期、销售金额、产品编号、客户编号等。每一行记录代表了一笔销售交易的具体信息。

  | 销售日期   | 产品编号 | 客户编号 | 销售金额 |
  | ---------- | -------- | -------- | -------- |
  | 2022-01-01 | P001     | C001     | 100      |
  | 2022-01-02 | P002     | C002     | 150      |
  | 2022-01-03 | P001     | C003     | 200      |

- **维度表**：产品维度表包含了每个产品的描述信息，如产品名称、产品类型等。每一行记录代表了一个产品的描述信息。

  | 产品编号 | 产品名称 | 产品类型 |
  | -------- | -------- | -------- |
  | P001     | 产品A    | 类型1    |
  | P002     | 产品B    | 类型2    |

在这个示例中，销售事实表存储了销售交易的具体信息，而产品维度表存储了产品的描述信息，两者通过产品编号进行关联。



## The difference of sources directory and seed directory

1. **sources文件夹**：
   - **作用**：用于定义和管理数据源（source）。
   - **内容**：sources文件夹中包含了用于连接到外部数据源的配置文件，例如连接信息、认证信息等。
   - **文件类型**：通常是YAML或JSON格式的配置文件，用于描述数据源的连接和相关设置。
   - **使用场景**：适用于连接外部数据源，如数据库、API等，并将其定义为dbt项目的数据源，以便在模型中使用。
2. **seed文件夹**：
   - **作用**：用于提供种子数据（seed data），即项目初始化时使用的静态数据。
   - **内容**：seed文件夹中包含了静态数据文件，通常是CSV或其他常见格式的数据文件，用于初始化数据模型。
   - **文件类型**：通常是静态数据文件，以常见的数据格式存储，如CSV、JSON等。
   - **使用场景**：适用于在项目初始化阶段加载静态数据，如参考数据、常量数据等，以便在模型中进行分析和处理。

简而言之，sources文件夹用于管理数据源的连接配置，而seed文件夹用于提供静态数据以初始化项目。这两个文件夹在dbt项目中起着不同的作用，但都是在数据处理过程中常见的组成部分。



## 4. Development of dbt models

### The - vars argument must be a YAML dictionary, but was of type str

Remember to add a space between the variable and the value. Otherwise, it won't be interpreted as a dictionary.

It should be:

```
dbt run --vars 'is_test_run: false'
```



```
SELECT
    locationid,
    borough,
    zone,
    replace(service_zone, 'Boro', 'Green') as service_zone
FROM {{ ref('taxi_zone_lookup) }}
```



### Explain ref()

The `ref()` function references underlying tables and views in the Data Warehouse. When compiled, it will automatically build the dependencies and resolve the correct schema fo us. So, if BigQuery contains a schema/dataset called `dbt_dev` inside the `my_project` database which we're using for development and it contains a table called `stg_green_tripdata`, then the following code...

```
WITH green_data AS (
    SELECT *,
        'Green' AS service_type
    FROM {{ ref('stg_green_tripdata') }}
),
```

...will compile to this:

```
WITH green_data AS (
    SELECT *,
        'Green' AS service_type
    FROM "my_project"."dbt_dev"."stg_green_tripdata"
),
```

- The `ref()` function translates our references table into the full reference, using the `database.schema.table` structure.
- If we were to run this code in our production environment, dbt would automatically resolve the reference to make ir point to our production schema.



## 5. Testing and documenting dbt models





## 6. Deploying a dbt project

### The problems I have met during this phase:

#### 1. Model configurations for a directory of models are not nested under the project name

To apply configurations to models within your project, you need to **nest configurations under the project name**, and then use the directory path to apply fine-grained configurations.

For example, consider a project, called `taxi_ride_ny` with the following structure:

```markdown
.
├── dbt_project.yml
└── models
    ├── staging
    │   ├── schema.yml
    │   ├── stg_green_tripdata.sql
    │   └── stg_yellow_tripdata.sql
    ├── core
    │   ├── schema.yml
    │   ├── dim_zones.sql
    │   └── fact_trips.sql
    .........

```

The following configuration is valid:

```yaml
name: 'taxi_ride_ny'
models:
  taxi_ride_ny: # Name of this dbt project
    staging:
      materialized: view # Applies to all files under models/staging
    core:
      materialized: table # Applies to all files under models/core

vars:
  payment_type_values: [1,2,3,4,5,6]

seeds:
  taxi_ride_ny: # Name of this dbt project
    taxi_zone_lookup:
      +column_types:
        locationid: numeric
```

The most common mistake people make is to omit the package name, like so:

```yaml
name: 'taxi_ride_ny'

seeds:
  # Missing the name of this dbt project
    taxi_zone_lookup:
      +column_types:
        locationid: numeric
```



Commonly used DBT command:

`dbt run`

`dbt run --select my_model.sql`: will only run the model itself

`dbt build`: To build all models and seeds

`dbt seed`: Dbt seeds are meant to be used with CSV files that contain data that will not be changed often. In our example, we copy the content of [taxi_zone_lookup.csv](https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/misc) and paste it in a file in the seeds directory. Then, we run `dbt seed` on the command line to create this table in our database.

`dbt deps`: when we need to use packages, we must first run this command to install all dependencies

`dbt test`: run all tests through the command





## 7. Locker studio

维度：横轴

指标：纵轴



## Homework 4 question 4:

```sql
with fhv as (
    select service_type, count(*) total_count
    from {{ ref('fact_fhv_trips') }}
    where extract(month from pickup_datetime) = 7
    group by service_type
),
green_yellow as (
    select service_type, count(*) total_count
    from {{ ref('fact_trips') }}
    where extract(month from pickup_datetime) = 7
    group by service_type
)

select * from fhv
union all
select * from green_yellow
```





# Module 5 Batch Processing



## Notes worth referring to

https://github.com/ziritrion/dataeng-zoomcamp/blob/main/notes/5_batch_processing.md

https://github.com/boisalai/de-zoomcamp-2023/blob/main/week5.md



## 1. Setup

### macOS + Anaconda

#### 1. Installing Java

Ensure Brew and Java installed in your system:

```zsh
xcode-select --install
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
brew install java
```



Add the following environment variables to your `.bash_profile` or `.zshrc`:

```
export JAVA_HOME=/opt/homebrew/opt/openjdk
export PATH="$JAVA_HOME/bin/:$PATH"

echo 'export PATH="/opt/homebrew/opt/openjdk/bin:$PATH"' >> ~/.zshrc
```



Make sure Java was installed to `/opt/homebrew/opt/openjdk`: Open Finder > Press Cmd+Shift+G > paste "/opt/homebrew/opt/openjdk". If you can't find it, then change the path location to appropriate path on your machine. You can also run `brew info java` to check where java was installed on your machine.



#### 2. Anaconda-based spark set up

if you are having anaconda setup, you can skip the spark installation and instead Pyspark package to run the spark. With Anaconda and Mac we can spark set by first installing pyspark and then for environment variable set up findspark

```zsh
pip3 install pyspark
pip3 install findspark
```



Ensure that open JDK is already set up. This allows us to not have to install Spark separately and manually set up the environment.

Also with this we may have to use Jupyter Lab (instead of Jupyter Notebook) to open a Jupyter notebook for running the programs. 

Once the Spark is set up start the conda environment and open Jupyter Lab. Run the program below in notebook to check everything is running fine.

```python
import pyspark
from pyspark.sql import SparkSession

!spark-shell --version

# Create SparkSession
spark = SparkSession.builder.master("local[1]") \
                    .appName('test-spark') \
                    .getOrCreate()

print(f'The PySpark {spark.version} version is running...')
```



### Some important concept

Spark is used for transforming data in a Data Lake.

There are tools such as Hive, Presto or Athena (a AWS managed Presto) that allow you to express jobs as SQL queries. However, there are times where you need to apply more complex manipulation which are very difficult or even impossible to express with SQL (such as ML models); in those instances, Spark is the tool to use.



### 开启 JupyterLab 代码自动提示功能

```
pip install jupyterlab-lsp
pip install 'python-lsp-server[all]'
```

进入 JupyterLab, 点击设置–高级设置–Code Completion–勾选 Continuous hinting



## 3. Spark SQL and DataFrames

### 3.1  First Look at Spark/PySpark

在读取 .csv.gz 文件的前 1001 行，并且将这 1001 行输出到一个新的 csv 文件中：

```zsh
zcat < fhvhv_tripdata_2021-01.csv.gz | head -n 1001  > head.csv
```

这部分命令使用 `zcat` 命令来解压缩名为 `fhvhv_tripdata_2021-01.csv.gz` 的文件



### 3.2 Spark DataFrames

Unlike CSV files, parquet files contain the schema of the dataset, so there is no need to specify a schema like we previously did when reading the CSV file. You can check the schema like this:

```python
df.printSchema()
```

One of the reasons why parquet files are smaller than CSV files is because they store the data according to the datatypes, so integer values will take less space than long or string values.



#### Action vs Transformations

Some Spark methods are "lazy", meaning that they are not executed right away. You can test this with the last instructions we run in the previous section: after running them, the Spark UI will not show any new jobs. However, running `df.show()` right after will execute right away and display the contents of the dataframe; the Spark UI will also show a new job.

These lazy commands are called ***transformations*** and the eager commands are called ***actions***. Computations only happen when actions are triggered.

**Transformations -- lazy (not executed immediately)**

- select colums
- filter
- joins
- group by
- .......

**Actions -- eager (executed immediately)**

- show
- take
- head
- write
- ......



#### Functions and User Defined Functions (UDFs)

Besides the SQL and Pandas-like commands we've seen so far, Spark provides additional built-in functions that allow for more complex data manipulation. By convention, these functions are imported as follows:

```
from pyspark.sql import functions as F
```



Here's an example of built-in function usage:

```
df \
    .withColumn('pickup_date', F.to_date(df.pickup_datetime)) \
    .withColumn('dropoff_date', F.to_date(df.dropoff_datetime)) \
    .select('pickup_date', 'dropoff_date', 'PULocationID', 'DOLocationID') \
    .show()
```

- `withColumn()`is a **transformation** that adds a new column to the dataframe.
  - ***IMPORTANT***: adding a new column with the same name as a previously existing column will overwrite the existing column!

- `select()` is another transformation that selects the stated columns.
- `F.to_date()` is a built-in Spark function that converts a timestamp to date format (year, month and day only, no hour and minute).

A list of built-in functions is available [in the official Spark documentation page](https://spark.apache.org/docs/latest/api/sql/index.html).



Besides these built-in functions, Spark allows us to create ***User Defined Functions*** (UDFs) with custom behavior for those instances where creating SQL queries for that behaviour becomes difficult both to manage and test.

UDFs are regular functions which are then passed as parameters to a special builder



### Spark SQL

`F.lit()` adds a *literal* or constant to a dataframe. We use it here to fill the `service_type` column with a constant value, which is its corresponging taxi type.



Note that the SQL query is wrapped with 3 double quotes (`"`).





## 4. Spark Internals

### 4.1. Anatomy of a Spark Cluster



### 4.2 GROUP BY in Spark

The second stage **shuffles** the data: Spark will put all records with the **same keys** (in this case, the GROUP BY keys which are hour and zone) in the **same partition**. The algorithm to do this is called external merge sort. Once the shuffling has finished, we can once again apply the GROUP BY to these new partitions and **reduce** the records to the **final output**.

- Note that the shuffled partitions may contain more than one key, but all records belonging to a key should end up in the same partition.



### 4.3 Joins in Spark





## 5. Resilient Distributed Datasets

#### mapPartitions() 和 map() 的区别

`map()` 和 `mapPartitions()` 都是Spark中用于RDD转换的函数，它们之间的主要区别在于处理数据的粒度和效率。

1. **map()：**
   - `map()` 函数对RDD中的每个元素都应用一个函数，返回一个新的RDD，该RDD包含应用函数后的结果。
   - `map()` 函数是一种逐元素转换操作，适用于需要对每个元素进行单独操作的场景。
   - 由于 `map()` 对每个元素都进行一次函数调用，因此在处理大规模数据时，可能会产生大量的函数调用开销，导致性能下降。
2. **mapPartitions()：**
   - `mapPartitions()` 函数是对RDD中的每个分区应用一个函数，返回一个新的RDD，该RDD包含应用函数后的结果。
   - `mapPartitions()` 函数是一种批量转换操作，适用于需要对每个分区进行操作的场景，因此可以减少函数调用的开销。
   - 在处理大规模数据时，`mapPartitions()` 通常比 `map()` 更高效，因为它将函数应用于每个分区而不是每个元素，减少了函数调用的次数。



## 6. Running Spark in the Cloud

### 6.1 Connecting to Google Cloud Storage



### 6.2. Creating a Local Spark Cluster

We will now see how to crate a Spark cluster in [Standalone Mode](https://spark.apache.org/docs/latest/spark-standalone.html) so that the cluster can remain running even after we stop running our notebooks.

Simply go to your Spark install directory from a terminal and run the following command:

`sbin` 文件夹的位置：`/opt/homebrew/Cellar/apache-spark/3.5.1/libexec`

```shell
./sbin/start-master.sh
```



You should now be able to open the main Spark dashboard by browsing to `localhost:8080` (remember to forward the port if you're running it on a virtual machine). At the very top of the dashboard the URL for the dashboard should appear; copy it and use it in your session code like so:

```shell
spark = SparkSession.builder \
    .master("spark://<URL>:7077") \
    .appName('test') \
    .getOrCreate()
```



You may note that in the Spark dashboard there aren't any *workers* listed. The actual Spark jobs are run from within ***workers*** (or *slaves* in older Spark versions), which we need to create and set up.

Similarly to how we created the Spark master, we can run a worker from the command line by running the following command from the Spark install directory:

```shell
./sbin/start-worker.sh <master-spark-URL>
```



最后运行的时候需要执行的命令：

```shell
spark-submit \
    --master="spark://<URL>" \
    my_script.py \
        --input_green='data/pq/green/2020/*/' \
        --input_yellow='data/pq/yellow/2020/*/' \
        --output='data/report-2020'
```





### 6.3. Setting up a Dataproc Cluster

在 Terminal 中运行 gcloud 相关命令来创建集群：

```shell
gcloud dataproc clusters create de-zoomcamp-cluster \
    --region=us-central1 \
    --subnet=default \
    --master-machine-type=n2-standard-4 \
    --num-workers=0 \
    --project=dtc-de-419107 \
    --optional-components=JUPYTER,DOCKER \
    --service-account=mage-zoomcamp@dtc-de-419107.iam.gserviceaccount.com
```

**为什么要在 terminal 中创建？**因为，当我们在 GCP WEB UI 中创建集群时，不可以手动选择要使用的 service account, 这时候，dataproc 服务就会使用默认的 compute engine service account 来执行。但是，创建集群会失败，因为这个默认的 service account 没有足够的权限（storage 相关权限）



#### Submit a job from UI

Just need to follow the referred instruction.

We have to upload `06_spark_sql.py` file to the bucket. Make sure you don’t specify the spark master in the code. The code to get a spark session should look like this.

```shell
gsutil cp 06_spark_sql.py gs://dtc_data_lake_de-zoomcamp-nytaxi-spark/code/06_spark_sql.py 
```





#### Submit a job with gloud CLI

Before, submit this command, we must add the role **Dataproc Administrator** to the permission **dtc-dez-user** created in the previous weeks.

```shell
gcloud dataproc jobs submit pyspark \
    --cluster=de-zoomcamp-cluster \
    --region=us-central1 \
    gs://dtc_data_lake_de-zoomcamp-nytaxi-spark/code/06_spark_sql.py \
    -- \
        --input_green='gs://dtc_data_lake_de-zoomcamp-nytaxi-spark/pq/green/2020/*/' \
        --input_yellow='gs://dtc_data_lake_de-zoomcamp-nytaxi-spark/pq/yellow/2020/*/' \
        --output='gs://dtc_data_lake_de-zoomcamp-nytaxi-spark/report-2020'
```





### 6.4. Connecting Spark to Big Query

https://cloud.google.com/dataproc/docs/tutorials/bigquery-connector-spark-example?hl=zh-cn#pyspark

First, we need to upload `06_spark_sql_bigquery.py` to GCP Bucket

```shell
gsutil cp 06_spark_sql_bigquery.py gs://dtc_data_lake_de-zoomcamp-nytaxi-spark/code/06_spark_sql_bigquery.py 
```

Then, we just need to execute the following gcloud command to submit spark job and directly write the output to Bigquery

```shell
gcloud dataproc jobs submit pyspark \
    --cluster=de-zoomcamp-cluster \
    --region=us-central1 \
    --jars=gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar \
    gs://dtc_data_lake_de-zoomcamp-nytaxi-spark/code/06_spark_sql_bigquery.py \
    -- \
        --input_green='gs://dtc_data_lake_de-zoomcamp-nytaxi-spark/pq/green/2020/*/' \
        --input_yellow='gs://dtc_data_lake_de-zoomcamp-nytaxi-spark/pq/yellow/2020/*/' \
        --output=trips_data_all.reports-2020
```

Go to **BigQuery**, we should see the report `reports-2020` created under `trips_data_all`.





## workshop 2

### Install PostgreSQL

`brew install postgresql`

To start postgresql@14 now and restart at login:

 `brew services start postgresql@14`



**Advantages of using RisingWave:**

1. instead of doing 1 million joins, we just do one join for the new record and then incrementally add this to the pre-saved results



### Homework solution:

#### Q1:

Create a materialized view to compute the average, min and max trip time **between each taxi zone**.

Note that we consider the do not consider `a->b` and `b->a` as the same trip pair. So as an example, you would consider the following trip pairs as different pairs:

```plaintext
Yorkville East -> Steinway
Steinway -> Yorkville East
```

From this MV, find the pair of taxi zones with the highest average trip time. You may need to use the [dynamic filter pattern](https://docs.risingwave.com/docs/current/sql-pattern-dynamic-filters/) for this.

Options:

1. **Yorkville East, Steinway**
2. Murray Hill, Midwood
3. East Flatbush/Farragut, East Harlem North
4. Midtown Center, University Heights/Morris Heights

p.s. The trip time between taxi zones does not take symmetricity into account, i.e. `A -> B` and `B -> A` are considered different trips. This applies to subsequent questions as well.

```sql
CREATE MATERIALIZED VIEW min_max_avg_trip_time_data AS
    with tmp as (
        SELECT
            t1.zone pickup_zone,
            t2.zone dropoff_zone,
            trip_data.tpep_dropoff_datetime - trip_data.tpep_pickup_datetime trip_time
        from
            trip_data
        join taxi_zone t1 on trip_data.pulocationid = t1.location_id
        join taxi_zone t2 on trip_data.dolocationid = t2.location_id
    )
    select
        pickup_zone,
        dropoff_zone,
        avg(trip_time) avg_trip_time,
        max(trip_time) max_trip_time,
        min(trip_time) min_trip_time
    from
        tmp
    group by
        pickup_zone, dropoff_zone;


with highest_avg_trip_time as (
    select
        avg_trip_time
    from
        min_max_avg_trip_time_data
    order by
        avg_trip_time desc
    limit 1
)
select
    pickup_zone,
    dropoff_zone,
    avg_trip_time
from
    min_max_avg_trip_time_data
WHERE
    avg_trip_time = (select avg_trip_time from highest_avg_trip_time);
```



#### Q2:

Recreate the MV(s) in question 1, to also find the **number of trips** for the pair of taxi zones with the highest average trip time.

Options:

1. 5
2. 3
3. 10
4. **1**

```sql
with highest_avg_trip_time as (
    select
        avg_trip_time
    from
        min_max_avg_trip_time_data
    order by
        avg_trip_time desc
    limit 1
)
select
    count(*) number_of_trips
from
    min_max_avg_trip_time_data
where
    avg_trip_time = (select avg_trip_time from highest_avg_trip_time);
```



#### Q3:

From the latest pickup time to 17 hours before, what are the top 3 busiest zones in terms of number of pickups? For example if the latest pickup time is 2020-01-01 17:00:00, then the query should return the top 3 busiest zones from 2020-01-01 00:00:00 to 2020-01-01 17:00:00.

HINT: You can use [dynamic filter pattern](https://docs.risingwave.com/docs/current/sql-pattern-dynamic-filters/) to create a filter condition based on the latest pickup time.

NOTE: For this question `17 hours` was picked to ensure we have enough data to work with.

Options:

1. Clinton East, Upper East Side North, Penn Station
2. **LaGuardia Airport, Lincoln Square East, JFK Airport**
3. Midtown Center, Upper East Side South, Upper East Side North
4. LaGuardia Airport, Midtown Center, Upper East Side North

```sql
with highest_avg_trip_time as (
    select
        max(tpep_pickup_datetime) latest_pickup_time
    from
        trip_data
),
tmp as (
    select
        pulocationid,
        count(*) num_of_pickups
    from
        trip_data
    join
        highest_avg_trip_time h
    on
        tpep_pickup_datetime >= h.latest_pickup_time - interval '17 hours'
        and
        tpep_pickup_datetime <= h.latest_pickup_time
    group by
        pulocationid
    order by
        2 desc
    limit 3
)

select
    taxi_zone.zone,
    tmp.num_of_pickups
from
    tmp
join
    taxi_zone
on
    tmp.pulocationid = taxi_zone.location_id
```
















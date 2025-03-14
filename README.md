# AWS Configuration Repository 📁  

## **Overview**  
This repository serves as the **source of truth for AWS deployments**, containing JSON-based configurations that define **what gets deployed**.  
- **No manual Terraform changes required** – deployments are controlled purely via config updates.  
- **Ensures full auditability** – every deployment is tied to Git commits, making changes transparent.  
- **Prevents unauthorized deployments** – if it’s not in this repo, Terraform won’t deploy it.  
- **Syncs to AWS Parameter Store** – allowing infrastructure components to dynamically discover their configurations.  

---

## **📂 Repository Structure**
```
aws-config/
│── dev/
│   │── vpc/
│   │   ├── main-vpc.json          # Defines main VPC configuration
│   │── aurora-postgres/
│   │   ├── main-db-A.json         # Defines primary Aurora DB for feature development A
│   │   ├── main-db-B.json         # Defines primary Aurora DB for feature development B
│   │   ├── main-db-C.json         # Defines primary Aurora DB for feature development C
│── prod/
│   │── vpc/
│   │   ├── main-vpc.json          # Defines main VPC configuration
│   │── aurora-postgres/
│   │   ├── main-db.json           # Defines primary Aurora DB
│── README.md
```

---

## **🚀 How It Works**
### **1️⃣ Configurations Define What Gets Deployed**
- Each AWS environment (dev, qa, prod) **has its own directory**.
- Each AWS component (VPC, RDS, Lambda) **has its own directory**.
- Each JSON file **defines a specific deployment instance**.
- Example: If `main-vpc.json` exists in `/vpc/`, it means **a VPC named "main-vpc" is deployable**.

---

### **2️⃣ Terraform Reads Configurations from AWS Parameter Store**
Before deploying, Terraform checks if a **config entry exists** in AWS Parameter Store.  
For example, when deploying a VPC named `"main-vpc"`, Terraform validates:
```
/aws/vpc/main-vpc/config   ✅ (Required for deployment)
/aws/vpc/main-vpc/runtime  ⏳ (Created after deployment)
```
If the **config is missing, Terraform will fail**, ensuring only pre-approved infrastructure gets deployed.

---

### **3️⃣ Syncing Configurations to AWS Parameter Store**
To make JSON configurations available to Terraform, run:
```sh
./scripts/sync-to-aws.sh
```
This script:
✅ Pushes all JSON configs to AWS Parameter Store  
✅ Ensures Parameter Store stays **in sync with the latest Git commits**  
✅ Enforces **deployment security** by preventing unauthorized infrastructure changes  

---

## **📖 Example: Defining a VPC**
### **1️⃣ Create a JSON Config File**
To define a VPC, create `/vpc/main-vpc.json`:
```json
{
  "vpc_cidr": "10.0.0.0/16",
  "enable_dns_support": true,
  "private_subnet_cidrs": ["10.0.1.0/24", "10.0.2.0/24"]
}
```
Commit and push this change to Git.

### **2️⃣ Sync to AWS Parameter Store**
```sh
./scripts/sync-to-aws.sh
```
This pushes `/aws/vpc/main-vpc/config` to AWS Parameter Store.

### **3️⃣ Terraform Validates Before Deployment**
Terraform checks AWS Parameter Store before proceeding:
```sh
terraform apply -var="nickname=main-vpc"
```
✅ If `/aws/vpc/main-vpc/config` exists, Terraform deploys.  
❌ If not, Terraform **fails**, ensuring **only approved infrastructure gets built**.

---

## **🔄 Supporting Multiple Environments & Feature Branches**
Because each deployment is **defined by a simple JSON file**, you can:
- **Deploy multiple versions side by side** (`main`, `feature-x`, `staging`).
- **Update infrastructure via Git commits**, rather than manual Terraform edits.
- **Easily track changes** – every deployment change is stored in version control.

---

## **🔐 Security & Compliance**
✅ **Full Auditability** – Every deployment change is tracked in Git.  
✅ **Prevents unauthorized changes** – Only **approved config updates** affect AWS infrastructure.  
✅ **Access Control via IAM** – Only **authorized users can sync configs to AWS Parameter Store**.  

---

## **📌 Next Steps**
Want to implement this in your AWS environment? Here’s what to do next:  
1️⃣ **Fork this repo and define your own configurations.**  
2️⃣ **Use the sync script to push configs to AWS Parameter Store.**  
3️⃣ **Deploy infrastructure using the [`aws-iac`](https://github.com/your-username/aws-iac) Terraform repo.**  

📩 **Questions? Reach out or contribute!**  
This is an open-source approach, and improvements are always welcome.  

---

📢 **Like this approach? Star the repo and follow for updates!** 🚀  

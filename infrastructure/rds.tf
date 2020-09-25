resource "aws_rds_cluster_instance" "cluster_instances" {
  identifier         = "${var.cluster_name}-instance"
  cluster_identifier = aws_rds_cluster.cluster.id
  instance_class     = var.instance_class
}

resource "aws_rds_cluster" "cluster" {
  cluster_identifier      = var.cluster_name
  database_name           = var.database_name
  master_username         = var.username
  master_password         = var.password
  vpc_security_group_ids  = [aws_security_group.aurora-sg.id]
  skip_final_snapshot     = true
  availability_zones      = ["us-east-1a", "us-east-1b", "us-east-1c"]
  engine                  = "aurora-mysql5.7"
  engine_version          = "5.7.12"
  backup_retention_period = 1
  preferred_backup_window = "07:00-09:00"
}

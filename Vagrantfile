# -*- mode: ruby -*-
# vi: set ft=ruby :

# Akri.dz — 5-node deployment
# Run: vagrant up
# Each node gets Docker pre-installed and the repo cloned automatically.
# Replace YOUR_GITHUB_USERNAME below before running.

GITHUB_REPO = "hamdiislem/akri.dz"

NODES = [
  { name: "node1", ip: "192.168.56.10", memory: 2048, cpus: 2, role: "infra"     },
  { name: "node2", ip: "192.168.56.11", memory: 1024, cpus: 1, role: "auth"     },
  { name: "node3", ip: "192.168.56.12", memory: 1024, cpus: 1, role: "api"      },
  { name: "node4", ip: "192.168.56.13", memory: 1024, cpus: 1, role: "frontend" },
  { name: "node5", ip: "192.168.56.14", memory:  512, cpus: 1, role: "worker"   },
]

PROVISION_DOCKER = <<-SHELL
  apt-get update -qq
  apt-get install -y -qq ca-certificates curl gnupg git
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
    > /etc/apt/sources.list.d/docker.list
  apt-get update -qq
  apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
  usermod -aG docker vagrant
  systemctl enable docker
  systemctl start docker
SHELL

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.box_check_update = false

  NODES.each do |node|
    config.vm.define node[:name] do |vm_config|
      vm_config.vm.hostname = node[:name]
      vm_config.vm.network "private_network", ip: node[:ip]

      vm_config.vm.provider "virtualbox" do |vb|
        vb.name   = "akri-#{node[:name]}"
        vb.memory = node[:memory]
        vb.cpus   = node[:cpus]
        vb.gui    = false
      end

      # Install Docker on every node
      vm_config.vm.provision "shell", inline: PROVISION_DOCKER

      # Clone the repo
      vm_config.vm.provision "shell", inline: <<-SHELL
        git clone https://github.com/#{GITHUB_REPO}.git /home/vagrant/akri.dz || true
        chown -R vagrant:vagrant /home/vagrant/akri.dz
      SHELL

      # Node-specific: start the right service
      case node[:role]
      when "infra"
        vm_config.vm.provision "shell", inline: <<-SHELL
          cd /home/vagrant/akri.dz/deployment/server1-infra
          docker compose up -d
        SHELL

      when "auth"
        vm_config.vm.provision "shell", inline: <<-SHELL
          cd /home/vagrant/akri.dz/deployment/server2-auth
          docker compose up -d --build
        SHELL

      when "api"
        vm_config.vm.provision "shell", inline: <<-SHELL
          cd /home/vagrant/akri.dz/deployment/server3-api
          docker compose up -d --build
        SHELL

      when "frontend"
        vm_config.vm.provision "shell", inline: <<-SHELL
          cd /home/vagrant/akri.dz/deployment/server4-frontend
          docker compose up -d --build
        SHELL

      when "worker"
        vm_config.vm.provision "shell", inline: <<-SHELL
          cd /home/vagrant/akri.dz/deployment/server5-worker
          docker compose up -d --build
        SHELL
      end
    end
  end
end

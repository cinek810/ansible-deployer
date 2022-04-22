FROM almalinux:latest


#RUN dnf update -y
RUN dnf install -y epel-release
RUN dnf install -y ansible python3 python3-pip
RUN dnf install -y bash openssh-server tar gzip git ca-certificates

RUN go get https://github.com/cinek810/ansible-deployer.git
RUN pip3.6 install .
ADD ./etc /etc/ansible-deployer
RUN groupadd test_group
RUN gpasswd -a root test_group


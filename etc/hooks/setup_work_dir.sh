#!/bin/bash -l

cat << END > ./runBinTrue.yaml
- hosts: all
  connection: "local"
  tasks:
      - name: "Run /bin/true"
        shell: "/bin/true"
END

cat << END > ./test_infra1_inv.yaml
localhost
END

cat << END > ./prod_infra1_inv.yaml
localhost
END

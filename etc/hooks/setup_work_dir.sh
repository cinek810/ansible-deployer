#!/bin/bash -l

cat << END > ./runBinTrue.yaml
- hosts: all
  connection: "local"
  tasks:
      - name: "Run /bin/true"
        shell: "/bin/true"
END

cat << END > ./test_infra1_inv.yaml
[testHosts]
testHost1
testHost2
testHost3

localhost
END

cat << END > ./test_infra2_inv.yaml
[xyzHosts]
xyzHost1
xyzHost2
xyzHost3
xyzHost12
xyzHost58

localhost
END

cat << END > ./prod_infra1_inv.yaml
localhost
END

make an HTTP connection to the ALB

```bash
cat <<EOF > loop.sh
#!/bin/bash

runtime="3 minute"
endtime=\$(date -ud "\$runtime" +%s)
totaltime=0

while [[ \$(date -u +%s) -le \$endtime ]]
do
    curl -I "$AlbUrl/?[1-100]" | grep HTTP
    echo "sleeping for 10 seconds"
    echo "total time running = \$totaltime seconds"
    ((totaltime=totaltime+10))
    sleep 10
done
EOF
```

while true
do
    TIMESTAMP=$(date +"%F %T")
    echo $TIMESTAMP "Running Carouge Monitor"
    python3 main.py -w carouge &> logs/carouge.log

    TIMESTAMP=$(date +"%F %T")
    echo $TIMESTAMP "Running Alicante Consumption Monitor"
    python3 main.py -w alicante-consumption &> logs/alicante-consumption.log

    TIMESTAMP=$(date +"%F %T")
    echo $TIMESTAMP "Running Alicante Salinity Monitor"
    python3 main.py -w alicante-salinity &> logs/alicante-salinity.log

    TIMESTAMP=$(date +"%F %T")
    echo $TIMESTAMP "Running Braila Consumption Monitor"
    python3 main.py -w braila-consumption &> logs/braila-consumption.log

    TIMESTAMP=$(date +"%F %T")
    echo $TIMESTAMP "Running Braila Anomaly Monitor"
    python3 main.py -w braila-anomaly &> logs/braila-anomaly.log

    TIMESTAMP=$(date +"%F %T")
    echo $TIMESTAMP "Running Monitor Analysis and Report Tool"
    python3 anaylsis.py
    echo "Finished"
    echo ""

    TIMESTAMP=$(date +"%F %T")
    echo $TIMESTAMP "Sleeping for almost a day"
    sleep 86000
done
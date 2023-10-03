# Install requests
sleep 2
echo '#### Installing requests module ####'
pip3 install requests
echo '#### Installation complete for requests module ####'

echo '\n\n'

sleep 2
echo '#### Starting publishing of events ####'
# Run the script
python3 scripts/publish_events.py

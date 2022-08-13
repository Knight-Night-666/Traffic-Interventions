netconvert -s osm.net.xml --plain-output-prefix plain
/usr/share/sumo/tools/xml/xml2csv.py plain.edg.xml
python3 $SUMO_HOME/tools/randomTrips.py -n osm.net.xml --fringe-factor 5 -r dua.rou.xml -p 0.4 --end 3600 --binomial 3 --validate --weights-prefix all_edges_example
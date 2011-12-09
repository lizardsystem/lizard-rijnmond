lizard-rijnmond
==========================================

lizard-rijnmond is a lizard-map plugin to show "Rijnmond-Drechtsteden" data in
http://www.deltaportaal.nl/ . That data means:

- A shapefile with areas (*dijkringen*).

- Netcdf files with data for those areas.

As a lizard-map plugin it needs to:

- Have a sidebar that allows browsing the information.

- Show the data on the map via an adapter, using the shapefile.


Investigation results of the netcdf files we got
------------------------------------------------

This is all terribly specific to the "deltaportaal" project and the data Nelen
& Schuurmans got, of course :-)

Result

Measure

Area

``Area.vak`` maps to ``Result.geo_ids[]``.

``Result.measure`` maps to ``Measure.code``.


Implementation idea
-------------------

Import the shapefile into postgres: create a custom model for that.

Import the result netcdfs and record the netcdf url. Link it to a measure and
a time.




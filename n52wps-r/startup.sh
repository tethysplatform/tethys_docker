#!/bin/bash

WPS_ROOT=/usr/share/tomcat7-wps/wpshome
WPS_USERS=$WPS_ROOT/WEB-INF/classes/users.xml
SERVICE_SKELETON=$WPS_ROOT/config/wpsCapabilitiesSkeleton.xml

# Make sure we have a user set up
if [ -z "$USERNAME" ]; then
  USERNAME=wps
fi

if [ -z "$PASSWORD" ]; then
  PASSWORD=wps
fi

# Setup the user
rm $WPS_USERS
echo '<?xml version="1.0" encoding="UTF-8"?>' > $WPS_USERS
echo '<UserRepository xmlns="http://www.52north.org/users" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.52north.org/users http://incubator.52north.org/maven/schemas/users/1.0/users.xsd">' >> $WPS_USERS
echo "    <User  username=\"$USERNAME\" password=\"$PASSWORD\" realname=\"$USERNAME\"/>" >> $WPS_USERS
echo '</UserRepository>' >> $WPS_USERS

# Setup service metadata
if [ -z "$NAME" ]; then
  NAME="Your name"
fi

if [ -z "$POSITION" ]; then
  POSITION="Your position"
fi

if [ -z "$PHONE" ]; then
  PHONE=""
fi

if [ -z "$FAX" ]; then
  FAX=""
fi

if [ -z "$ADDRESS" ]; then
  ADDRESS=""
fi

if [ -z "$CITY" ]; then
  CITY=""
fi

if [ -z "$STATE" ]; then
  STATE=""
fi

if [ -z "$POSTAL_CODE" ]; then
  POSTAL_CODE=""
fi

if [ -z "$COUNTRY" ]; then
  COUNTRY=""
fi

if [ -z "$EMAIL" ]; then
  EMAIL=""
fi

sed "s=<ows:IndividualName>Your name</ows:IndividualName>=<ows:IndividualName>$NAME</ows:IndividualName>=g" -i $SERVICE_SKELETON
sed "s=<ows:PositionName>Your position</ows:PositionName>=<ows:PositionName>$POSITION</ows:PositionName>=g" -i $SERVICE_SKELETON
sed "s=<ows:Voice></ows:Voice>=<ows:Voice>$PHONE</ows:Voice>=g" -i $SERVICE_SKELETON
sed "s=<ows:Facsimile></ows:Facsimile>=<ows:Facsimile>$FAX</ows:Facsimile>=g" -i $SERVICE_SKELETON
sed "s=<ows:DeliveryPoint></ows:DeliveryPoint>=<ows:DeliveryPoint>$ADDRESS</ows:DeliveryPoint>=g" -i $SERVICE_SKELETON
sed "s=<ows:City></ows:City>=<ows:City>$CITY</ows:City>=g" -i $SERVICE_SKELETON
sed "s=<ows:AdministrativeArea></ows:AdministrativeArea>=<ows:AdministrativeArea>$STATE</ows:AdministrativeArea>=g" -i $SERVICE_SKELETON
sed "s=<ows:PostalCode></ows:PostalCode>=<ows:PostalCode>$POSTAL_CODE</ows:PostalCode>=g" -i $SERVICE_SKELETON
sed "s=<ows:Country></ows:Country>=<ows:Country>$COUNTRY</ows:Country>=g" -i $SERVICE_SKELETON
sed "s=<ows:ElectronicMailAddress></ows:ElectronicMailAddress>=<ows:ElectronicMailAddress>$EMAIL</ows:ElectronicMailAddress>=g" -i $SERVICE_SKELETON

/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
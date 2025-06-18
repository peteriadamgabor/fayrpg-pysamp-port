#define FILTERSCRIPT

#include <open.mp>
#include <colandreas>
#include <strlib>

forward GetVehicleColor1(vehicleid);
forward GetVehicleColor2(vehicleid);
forward PyFindZUpper(Float:x, Float:y);
forward PyFindZDown(Float:x, Float:y);

public OnFilterScriptInit()
{
	printf(" ");
	printf("-------------------------------------");
	printf("ColAndreas wapper for PySAMP loeaded!");
	printf("-------------------------------------");
	printf(" ");
}

public PyFindZUpper(Float:x, Float:y)
{
	new Float:z, result, output[2][16], string[16];
	CA_RayCastLine(x, y, 700.0, x, y, -1000.0, x, y, z);
	format(string, sizeof(string), "%f", z);
	strexplode(output, string, ".");
	result = strval(output[0]);
	return result;	
}

public PyFindZDown(Float:x, Float:y)
{
	new Float:z, result, output[2][16], string[16];
	CA_RayCastLine(x, y, 700.0, x, y, -1000.0, x, y, z);
	format(string, sizeof(string), "%f", z);
	strexplode(output, string, ".");
	result = strval(output[1]);
	return result;	
}

public GetVehicleColor1(vehicleid)
{
	new colour1, colour2;
    GetVehicleColours(vehicleid, colour1, colour2);
    return colour1;
}

public GetVehicleColor2(vehicleid)
{
	new colour1, colour2;
    GetVehicleColours(vehicleid, colour1, colour2);
    return colour2;
}

public OnFilterScriptExit()
{
	printf(" ");
	printf("  -----------------------------------");
	printf("  ColAndreas wapper for PySAMP unloeaded!");
	printf("  -----------------------------------");
	printf(" ");
}

from onem2m import AE, Constant

cli = AE.ClientLib()

arg = {Constant.CONST.ADN.ID:'S111115', Constant.CONST.ADN.NAME:'S111115', Constant.CONST.CHECK.URI:"S111115",
    Constant.CONST.SENSOR.ID:'111111', Constant.CONST.SENSOR.NAME:'Temp', Constant.CONST.SENSOR.HISTORY:11}

arg1 = {Constant.CONST.ADN.ID:'S111115', Constant.CONST.SENSOR.ID:'111111',Constant.CONST.SENSOR.NAME:'Temp',
    Constant.CONST.SENSING.NAME:'R1',Constant.CONST.SENSING.VALUE:32}

arg2 = {}
arg2['ADN.ID'] = 'S111115'
arg2['ID'] = '111111'
print('1 --------------')
print(cli.checkDuplicated(arg))
print('2 --------------')
print(cli.createADN(arg))
print('3 --------------')
print(cli.registrySensor(arg))
print('4 --------------')
print(cli.sendSensingReport(arg1))
print('5 --------------')
print(cli.getLastValue(arg2))
print('6 --------------')
print(cli.getValues(arg2))
print('7 --------------')
print(cli.getADNAll())
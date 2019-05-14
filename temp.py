from onem2m import AE

cli = AE.ClientLib()

json = {}
json['ADN.ID'] = 'S0.2.481.2.100.0.41.43_AE_test001'
json['ADN.NAME'] = 'Multisensor Device'
json['CHECK.URI'] = 'S0.2.481.2.100.0.41.43_AE_test001'
result = cli.checkDuplicated(json)
if result == 404:
    result = cli.createADN(json)
    print('> Result - create ADN: ', result)
elif result == 200:
    print('> Result - already registered ADN: ', result)
else:
    print('> Result - Internal server error: ', result)


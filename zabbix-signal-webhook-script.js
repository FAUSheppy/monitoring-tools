try {

    var params = JSON.parse(value);
    Zabbix.log(4, '[ Signal Webhook ] Executed with params: ' + params.URL + ', ' + params.Message);

    if (!params.URL) {
        throw 'Cannot get url';
    }

    fields = { 
        message : params.Message,
        number : params.number
    }

    var req = new HttpRequest();
    req.addHeader('Content-Type: application/json');

    var resp = req.post(params.URL, JSON.stringify(fields))
    return 'OK';

}
catch (error) {
    Zabbix.log(3, '[ Signal Webhook ] ERROR: ' + error);
    throw 'Sending Signal Message failed: ' + error;
}

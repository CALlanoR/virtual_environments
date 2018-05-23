var osquery = require('osquery');

var os = osquery.createClient({ path: '/var/osquery/osquery.em' });
os.query('select timestamp from time', function(err, res) {
  console.log(res);
});
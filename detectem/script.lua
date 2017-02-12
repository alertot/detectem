function main(splash)
  splash.response_body_enabled = true

  local url = splash.args.url
  assert(splash:go(url))
  assert(splash:wait(5))

  local detectFunction = [[
    detect = function(){
      var rs = [];

      softwareData.forEach(function(s) {
        var matchers = s.matchers;

        for (var i in matchers) {
          if (eval(matchers[i].check)){
            var version = eval(matchers[i].version);
            if (version) {
              rs.push({'name': s.name, 'version': version});
            }
          }
        }

      });

      return rs;
    }
  ]]
  splash:runjs('softwareData = $js_data;')
  splash:runjs(detectFunction)
  local softwares = splash:evaljs('detect()')

  return {
    har = splash:har(),
    softwares=softwares,
  }
end


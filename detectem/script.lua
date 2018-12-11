function main(splash)
  splash.images_enabled = false
  splash.response_body_enabled = true

  local url = splash.args.url
  splash:go(url)
  assert(splash:wait(5))

  local detectFunction = [[
    detect = function(){
      var rs = [];

      softwareData.forEach(function(s) {
        var matchers = s.matchers;
        var presenceFlag = false;

        for (var i in matchers) {
          var check_statement = matchers[i].check_statement
          var version_statement = matchers[i].version_statement

          if (eval(check_statement)){
            if (!version_statement){
              presenceFlag = true;
              continue;
            }

            var version = eval(version_statement);
            if (version) {
              rs.push({'name': s.name, 'version': version});
            }
          }
        }

        if (presenceFlag) {
          rs.push({'name': s.name})
        }

      });

      return rs;
    }
  ]]
  splash:runjs('softwareData = $js_data;')
  splash:runjs(detectFunction)

  local softwares = {}
  local scripts = {}
  local errors = {}

  local ok, res = pcall(splash.evaljs, self, 'detect()')
  if ok then
    softwares = res
  else
    errors['evaljs'] = res
  end

  local ok, res = pcall(splash.select_all, self, 'script')
  if ok then
    if res then
      for _, s in ipairs(res) do
        scripts[#scripts+1] = s.node.innerHTML
      end
    end
  else
    errors['select_all'] = res
  end

  return {
    har = splash:har(),
    softwares=softwares,
    scripts=scripts,
    errors=errors,
  }
end

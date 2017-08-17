function main(splash)
  splash.images_enabled = false
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


#! /usr/bin/env node
// http://mango-is.com/blog/engineering/pre-render-d3-js-charts-at-server-side.html
var d3 = require("d3"),
    jsdom = require("jsdom"),
    fs = require("fs");

function makeD3(output, callback) {
  if (arguments.length == 1) {
    callback = output;
    output = null;
  }

  jsdom.env({
    features: { QuerySelector: true },
    html: "<div></div>",
    scripts: [
      "./static/vendor/lodash.min.js",
      "./static/vendor/d3.min.js",
    ],
    done: function(errors, window) {
      if (errors && errors.length > 0) {
        console.log(errors);
      }
      var document = window.document,
          $ = document.querySelector.bind(document),
          parent = $("div");

      callback(d3, parent);

      var result = parent.innerHTML;

      if (output) {
        fs.writeFile(output, result, function(err) {
          if (err) {
            console.log("Error saving file", output, err);
          } else {
            console.log("Saved as", output);
          }
        });
      }
    },
  });
}

// test
makeD3("test.html", function (d3, root) {
  d3.select(root)
    .append("svg:svg")
    .attr("width", 600).attr("height", 300)
    .append("circle")
      .attr("cx", 300)
      .attr("cy", 150)
      .attr("r", 30)
      .attr("fill", "#26963c");
});

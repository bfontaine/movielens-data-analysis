#! /usr/bin/env node
// http://mango-is.com/blog/engineering/pre-render-d3-js-charts-at-server-side.html
var d3 = require("d3"),
    jsdom = require("jsdom"),
    http = require("http"),
    url = require("url"),
    _ = require("lodash"),

    host = "localhost",
    port = 1337;

function setupD3(callback) {
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
    },
  });
}

var routes = {};

http.createServer(function (req, res) {
  var method = req.method,
      path = url.parse(req.url).path,

      desc = method + " " + path;

  var fn = routes[desc];

  if (fn) {
    console.log(desc);

    var body = "";

    req.on("data", function(data) { body += data; });
    return req.on("end", function() {
      return fn(body, res);
    });
  }

  res.statusCode = 404;
  console.log(desc, "--> 404");
}).listen(port, host);
console.log("Listening on", host, "on port", port);

function route(path, fn) { routes[path] = fn; }

route("POST /draw/bipartite", function drawBipartite(body, res) {

  // { user1 -> [ movie1, movie2, ... ],
  //   user2 -> [ movie2, movie4, ... ],
  //   ...
  // }
  var data = JSON.parse(body);

  setupD3(function(d3, parent) {
    var svg = d3.select(parent).append("svg:svg"),
        width = 1200,
        height = 800;

    var force = d3.layout.force()
      .charge(-40)
      .linkDistance(20)
      .gravity(0.3)
      .size([width/2, height/2]); // just to be sure it fits

    svg.attr("width", width)
       .attr("height", height);

    var nodes = [],
        links = [],
        nodes_set = {},
        nodes_idx = {};

    // deduplicate nodes
    _.each(data, function(movies, user) {
      nodes_set[user] = -1;
      _.each(movies, function(movie) { nodes_set[movie] = -1; });
    });

    _.each(nodes_set, function(_, id) {
      var l = nodes.push({
        id: id,
        name: id,
        is_movie: id[0] == "m",
      });

      // store the index
      nodes_set[id] = l-1;
    });

    _.each(data, function(movies, user) {
      _.each(movies, function(movie) {
        var idx1 = nodes_set[user],
            idx2 = nodes_set[movie];

        links.push({source: idx1, target: idx2, weight: 1});
      });
    });

    force.nodes(nodes)
         .links(links);

    force.start()

    var maxTicks = 600;
    for (var i=0; i<maxTicks; i++) {
      // console.log("tick", i, "out of", maxTicks);
      force.tick();
    }

    force.stop()

    /*
    svg.selectAll(".link")
      .data(links)
      .enter().append("line")
        .attr("class", "link")
        .style("stroke", "#AAA")
        .attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });
    // */

    svg.selectAll(".node")
      .data(nodes)
      .enter().append("circle")
        .attr("class", "node")
        .attr("r", function(d) { return d.is_movie ? 3 : 3 })
        .style("fill", function(d) {
          return d.is_movie ? "blue" : "green"; // experimental
        })
      .attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; });

    res.writeHead(200, {"Content-Type": "image/svg+xml"});
    res.end(parent.innerHTML);
  });
});

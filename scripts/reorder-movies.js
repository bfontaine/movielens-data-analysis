var fs = require("fs"),
    reorder = require("reorder.js");

fs.readFile("/tmp/m.json", function(err, data) {
  var matrix = JSON.parse(data);
  var perm = reorder.optimal_leaf_order()(matrix);
  var matrix2 = reorder.stablepermute(matrix, perm);

  fs.writeFile("ordered-matrix.json", JSON.stringify(matrix2), function() {
    console.log("Done!");
  });
});

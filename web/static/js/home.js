var graph_data = document.getElementById("graph_json").textContent,

    width = 720,
    height = 500,

    force = d3.layout.force()
          .charge(-120)
          .linkDistance(30)
          .size([width, height]),

    parent = d3.select("graph"),
    svg = parent.append("svg")
          .attr("width", width)
          .attr("height", height);

// TODO

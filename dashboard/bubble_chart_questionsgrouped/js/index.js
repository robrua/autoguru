var json = {
  'children': [
    {'name': 'I\'m getting a 404 error. Can someone help?', 'value': 3},
    {'name': 'How do I get the Summoner ID by Account Name?', 'value': 16},
    {'name': 'How do I get experts for certain champions?', 'value': 15},
    {'name': 'Rate Limiting', 'value': 2},
    {'name': 'Cannot find data about passive skills.', 'value': 1},
    {'name': 'What does PlayerScore mean?', 'value': 3},
    {'name': 'Static Data 403 Forbidden', 'value': 1},
  ]
}

var diameter = 600,
    color = d3.scaleOrdinal(d3.schemeCategory20c);

var colorScale = d3.scaleLinear()
  .domain([0, d3.max(json.children, function(d) {
    return d.value;
  })])
  .range(["rgb(46, 73, 123)", "rgb(71, 187, 94)"]);

var bubble = d3.pack()
  .size([diameter, diameter])
  .padding(5);

var margin = {
  left: 0,
  right: 260,
  top: 0,
  bottom: 0
}

var svg = d3.select('#chart').append('svg')
  .attr('viewBox','0 0 ' + (diameter + margin.right) + ' ' + diameter)
  .attr('width', (diameter + margin.right))
  .attr('height', diameter)
  .attr('class', 'chart-svg');

var root = d3.hierarchy(json)
  .sum(function(d) { return d.value; })
  .sort(function(a, b) { return b.value - a.value; });

bubble(root);

var node = svg.selectAll('.node')
  .data(root.children)
  .enter()
  .append('g').attr('class', 'node')
  .attr('transform', function(d) { return 'translate(' + d.x + ' ' + d.y + ')'; })
  .append('g').attr('class', 'graph');

node.append("circle")
  .attr("r", function(d) { return d.r; })
  .style("fill", function(d) {
    return color(d.data.name);
  });

node.append("text")
  .attr("dy", ".3em")
  .style("text-anchor", "middle")
  .text(function(d) { return d.data.value; })
  .style("fill", "#ffffff");

svg.append("g")
  .attr("class", "legendOrdinal")
  .attr("transform", "translate(600,40)");

var legendOrdinal = d3.legendColor()
  .shape("path", d3.symbol().type(d3.symbolSquare).size(150)())
  .shapePadding(20)
  .scale(color);

svg.select(".legendOrdinal")
  .call(legendOrdinal);

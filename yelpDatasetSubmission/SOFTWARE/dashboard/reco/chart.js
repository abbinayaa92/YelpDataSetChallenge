var circles = function(business_name) {
  var chart, clear, click, hit, colpad, updEvents, data, force, gradient, gradientValue, fall, hashchange, height, id, jitter, label, link, margin, maxRadius, colr, mouseout, mouseover, name, node, scale, radius, textValue, tick, dataLoad, update, updateActive, updateLabels, updateNodes, width;
  
  data = [];
  name = business_name;
  width = window.innerWidth/1.1;
  height = window.innerHeight * 0.5;
  colpad = 4;
  colr = 12;
  jitter = 0.2;
  node = null;
  label = null;
  margin = {
    top: 0,
    right: 0,
    bottom: 0,
    left: 0
  };
  var tooltip = d3.select("body")
    .append("div")
    .style("position", "absolute")
    .style("z-index", "10")
    .style("visibility", "hidden")
    .style("color", "white")
    .style("padding", "8px")
    .style("background-color", "rgba(0, 0, 0, 0.75)")
    .style("border-radius", "6px")
    .style("font", "12px sans-serif")
    .text("tooltip");
  
   tick = function(e) {
    var alp;
    alp = e.alpha * 0.15;
    // node.attr("cx", function(d) { return d.x = Math.max(radius(d) / 4, Math.min(width, d.x)); }) .attr("cy", function(d) { return d.y = Math.max(radius(d), Math.min(height - radius(d), d.y)); });
    node.each(fall(alp)).each(hit(jitter)).attr("transform", function(d) {
      return "translate(" + d.x + "," + d.y + ")";
    });
    return label.style("left", function(d) {
      return ((margin.left + d.x) - d.dx / 2) + "px";
    }).style("top", function(d) {
      return ((margin.top + d.y) - d.dy / 2) + "px";
    });
  };
  force = d3.layout.force()
    .gravity(0)
    .charge(0)
    .size([width, height])
    .on("tick", tick);
      
  maxRadius = 65;
  scale = d3.scale.sqrt().range([0, maxRadius]);
   xStartValue = function(d) {
    return d.positiveProbability;
  };
  textValue = function(d) {
    return d.word;
  };
  radius = function(d) {
    return Number(d.business["frequency"]);
  };
  id = function(d) {
    return d.word.replace(/ /g,"-");
  };
  negative = function(d) {
    return Number(d.negativeProbability*100).toFixed(2);
  };
  positive = function(d) {
    return Number(d.positiveProbability*100).toFixed(2);
  };
  reviewIds = function(d) {
    return d.business.reviews.id;
  }
  Updgradient = function(d) {
    return id(d) + "-sentiment";
  };
  
  
   
  dataLoad = function(rawData) {
    location.replace("#");
    $.each(rawData,function(key, d) {
      d.countOverall = Number(d.business["frequency"]);
      d.positiveProbability = Number(d.positiveProbability);
      d.negativeProbability = Number(d.negativeProbability);
      return rawData.sort(function() {
        return 0.5 - Math.random();
      });
    });
    return rawData;
  };
  
  fall = function(alpha) {
    var ax, ay, cx, cy;
    cx = width / 2;
    cy = height / 2;
    ax = alpha / 8;
    ay = alpha;
    return function(d) {
      d.x += (cx - d.x) * ax;
      return d.y += (cy - d.y) * ay;
    };
  };
  
  createMix = function(d) {
    var svg = d3.select('svg#show-main');
    // Define the gradient
    
    gradient = svg.append("svg:defs")
        .attr("id", Updgradient(d))
        .append("svg:linearGradient")
        .attr("id", Updgradient(d) + "-gradient")
        .attr("x1", "0%")
        .attr("y1", "0%")
        .attr("x2", "100%")
        .attr("y2", "0%")
        .attr("spreadMethod", "pad");
    gradient.append("svg:stop")
        .attr("offset", positive(d).toString() + "%")
        .attr("stop-color", "#a1d99b")
        .attr("stop-opacity", 1);
    gradient.append("svg:stop")
        .attr("offset", positive(d).toString() + "%")
        .attr("stop-color", "#fc9272")
        .attr("stop-opacity", 1);
    return 'url(#' + Updgradient(d) + '-gradient)';
  };
  
  updateMix = function(d) {
    var svg = d3.select('svg#show-main');
    var oldGradDef = d3.select('#' + Updgradient(d)).remove();

    // Define the gradient
    gradient = svg.append("svg:defs")
        .attr("id", Updgradient(d))
        .append("svg:linearGradient")
        .attr("id", Updgradient(d) + "-gradient")
        .attr("x1", "0%")
        .attr("y1", "0%")
        .attr("x2", "100%")
        .attr("y2", "0%")
        .attr("spreadMethod", "pad");
    gradient.append("svg:stop")
        .attr("offset", positive(d).toString() + "%")
        .attr("stop-color", "#31a354")
        .attr("stop-opacity", 1);
    gradient.append("svg:stop")
        .attr("offset", positive(d).toString() + "%")
        .attr("stop-color", "#de2d26")
        .attr("stop-opacity", 1);
    return 'url(#' + Updgradient(d) + '-gradient)';
  };
  
  resetMix = function(d) {
    var svg = d3.select('svg#show-main');
    var oldGradDef = d3.select('#' + Updgradient(d)).remove();

    gradient = svg.append("svg:defs")
        .attr("id", Updgradient(d))
        .append("svg:linearGradient")
        .attr("id", Updgradient(d) + "-gradient")
        .attr("x1", "0%")
        .attr("y1", "0%")
        .attr("x2", "100%")
        .attr("y2", "0%")
        .attr("spreadMethod", "pad");
    gradient.append("svg:stop")
        .attr("offset", positive(d).toString() + "%")
        .attr("stop-color", "#a1d99b")
        .attr("stop-opacity", 1);
    gradient.append("svg:stop")
        .attr("offset", positive(d).toString() + "%")
        .attr("stop-color", "#fc9272")
        .attr("stop-opacity", 1);
    return 'url(#' + Updgradient(d) + '-gradient)';
  };
  
 
 
 
  chart = function(selection) {
    return selection.each(function(rawData) {
      var maxDomainValue, svg, svgEnter;
      data = dataLoad(rawData);
      maxDomainValue = d3.max(data, function(d) {
        return radius(d);
      });
      scale.domain([0, maxDomainValue]);
      svg = d3.select(this).selectAll("svg").data([data]);
      svgEnter = svg.enter().append("svg");
      svg.attr("width", width );//+ margin.left + margin.right);
      svg.attr("height", height + margin.top + margin.bottom);
      svg.attr("id", "show-main");
      // svg.append("svg:defs").attr("id", "sentiment-gradients");
      node = svgEnter.append("g").attr("id", "circle-nodes").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
      node.append("rect").attr("id", "circle-background").on("click", clear);
      label = d3.select(this).selectAll("#circle-labels").data([data]).enter().append("div").attr("id", "circle-labels");
      update();
      hashchange();
      return d3.select(window).on("hashchange", hashchange);
    });
  };
  
  chart.jitter = function(_) {
    if (!arguments.length) {
      return jitter;
    }
    jitter = _;
    force.start();
    return chart;
  };
  chart.height= height;
  chart.width = width;
  chart.r = radius;
  
  
  update = function() {
    data.forEach(function(d, i) {
      return d.forceR = Math.max(colr, scale(radius(d)));
    });
    force.nodes(data).start();
    updateNodes();
    return updateLabels();
  };
  
  updateNodes = function() {
    node = node.selectAll(".circle-node").data(data, function(d) {
      return id(d);
    });
    node.exit().remove();
    return node.enter().append("a").attr("class", "circle-node").attr("xlink:href", function(d) {
      return "#" + (encodeURIComponent(id(d)));
    }).call(force.drag).call(updEvents).append("circle").attr("r", function(d) {
      return scale(radius(d));
    })
    // Fill the circle with the gradient
    .attr('fill', function(d) {
      return createMix(d);
    });
  };
  
  updateLabels = function() {
    var labelEnter;
    label = label.selectAll(".circle-label").data(data, function(d) {
      return id(d);
    });
    label.exit().remove();
    labelEnter = label.enter().append("a").attr("class", "circle-label").attr("href", function(d) {
      return "#" + (encodeURIComponent(id(d)));
    }).call(force.drag).call(updEvents);
    labelEnter.append("div").attr("class", "circle-label-name").text(function(d) {
      return textValue(d);
    });
    labelEnter.append("div").attr("class", "circle-label-value").text(function(d) {
      return radius(d);
    });
    label.style("font-size", function(d) {
      return Math.max(8, scale(radius(d) / 3.5)) + "px";
    }).style("width", function(d) {
      return 2.5 * scale(radius(d)) + "px";
    });
    label.append("span").text(function(d) {
      return textValue(d);
    }).each(function(d) {
      return d.dx = Math.max(2.5 * scale(radius(d)), this.getBoundingClientRect().width);
    }).remove();
    label.style("width", function(d) {
      return d.dx + "px";
    });
    return label.each(function(d) {
      return d.dy = this.getBoundingClientRect().height;
    });
  };
  
 
  
  updEvents = function(d) {
    d.on("click", click);
    d.on("mouseover", mouseover);
    return d.on("mouseout", mouseout);
  };
  clear = function() {
    return location.replace("#");
  };
  click = function(d) {
    location.replace("#" + encodeURIComponent(id(d)));
    return d3.event.preventDefault();
  };
    hashchange = function() {
    var id;
    id = decodeURIComponent(location.hash.substring(1)).trim();
    return updateActive(id);
  };
  updateActive = function(idValue) {
    // Set the new active gradient
    var currentNode;
    d3.selectAll(".circle-node").attr('fill', function(d) {
      if (id(d) == idValue) {
        currentNode = d;
        return updateMix(d);
      } else {
        return resetMix(d);
      };
    });
    node.classed("circle-selected", function(d) {
      return idValue === id(d);
    });
    if (idValue.length > 0) {
      showRev(currentNode, idValue)
    }
  };
  
   hit = function(force) {
    return function(d) {
      return data.forEach(function(d2) {
        var distance, minDistance, moveX, moveY, x, y;
        if (d !== d2) {
          x = d.x - d2.x;
          y = d.y - d2.y;
          distance = Math.sqrt(x * x + y * y);
          minDistance = d.forceR + d2.forceR + colpad;
          if (distance < minDistance) {
            distance = (distance - minDistance) / distance * force;
            moveX = x * distance;
            moveY = y * distance;
            d.x -= moveX;
            d.y -= moveY;
            d2.x += moveX;
            return d2.y += moveY;
          }
        }
      });
    };
  };
  
  showRev = function(currentNode, id) {

    var reviewList = currentNode.business["reviews"]
    var json;
    var items = [];
    var review =  "http://127.0.0.1:28017/yideas/review/?";
    var reviewRating =  "http://127.0.0.1:28017/yideas/reviewRating/?";
    var reviewRatingData;
     $.ajaxSetup( { "async": false } );
   for(i=0;i<reviewList.length;i++) {
   				var review =  "http://127.0.0.1:28017/yideas/review/?filter_review_id="+reviewList[i];
    			var reviewRating =  "http://127.0.0.1:28017/yideas/reviewRating/?filter_id="+reviewList[i];
    			$.getJSON(encodeURI(review), function(data) {
    			
    			 $.each(data.rows, function(index, item) {
    			$.getJSON(encodeURI(reviewRating), function(data1) {
    			
    			 $.each(data1.rows, function(index1, item1) { 
    			  console.log("review id:"+item.review_id)
				 var rating = Number(item1.rating).toFixed(2)
				 console.log(rating)
				 var reviewText = item.text

                 items.push( "<dt> <strong>Rating: " + rating + "</strong></dt>" + "<dd id='review-text'>" + reviewText + "</dd><br>" );

		});

      });
      $('.review-list').remove()
      $( "<ul>", {
        "class": "review-list",
        html: items.join( "" )
      }).appendTo( "#review" );
    });
	});
	}
	
	$.ajaxSetup( { "async": true } );
  };


  mouseover = function(d) {


    tooltip.style("top", (d3.event.pageY-10)+"px").style("left",(d3.event.pageX+10)+"px");
    
  	tooltip.text("positive : " + positive(d)+"%  negative : " + negative(d)+"%");
	tooltip.style("visibility", "visible");
    return node.classed("circle-hover", function(p) {
      return p === d;
    });
  };
  mouseout = function(d) {
  tooltip.style("visibility", "hidden")
    return node.classed("circle-hover", false);
  };
  function findElement(arr, propName, propValue) {
  for (var i=0; i < arr.length; i++)
  {
    if (arr[i][propName] == propValue)
      return arr[i];
      }
}
  
  return chart;
};

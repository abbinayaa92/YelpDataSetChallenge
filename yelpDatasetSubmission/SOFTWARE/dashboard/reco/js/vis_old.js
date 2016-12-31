var Bubbles = function(business_name) {
  var chart, clear, click, collide, collisionPadding, connectEvents, data, force, gradient, gradientValue, gravity, hashchange, height, idValue, jitter, label, link, margin, maxRadius, minCollisionRadius, mouseout, mouseover, name, node, rScale, rValue, textValue, tick, transformData, update, updateActive, updateLabels, updateNodes, width;
  width = window.innerWidth;
  height = window.innerWidth * 600 / 980 * 13 / 20;
  data = [];
  name = business_name;
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
    
  maxRadius = 65;
  rScale = d3.scale.sqrt().range([0, maxRadius]);
  rValue = function(d) {
    return Number(d.business["frequency"]);
  };
  idValue = function(d) {
    return d.word.replace(/ /g,"-");
  };
  nSentimentValue = function(d) {
    return Number(d.negativeProbability*100).toFixed(2);
  };
  pSentimentValue = function(d) {
    return Number(d.positiveProbability*100).toFixed(2);
  };
  reviewIds = function(d) {
    return d.business.reviews.id;
  }
  gradientId = function(d) {
    return idValue(d) + "-sentiment";
  };
  createGradientValue = function(d) {
    var svg = d3.select('svg#vis-main');
    // Define the gradient
    
    gradient = svg.append("svg:defs")
        .attr("id", gradientId(d))
        .append("svg:linearGradient")
        .attr("id", gradientId(d) + "-gradient")
        .attr("x1", "0%")
        .attr("y1", "0%")
        .attr("x2", "100%")
        .attr("y2", "0%")
        .attr("spreadMethod", "pad");

    // Define the gradient colors
    gradient.append("svg:stop")
        .attr("offset", pSentimentValue(d).toString() + "%")
        .attr("stop-color", "#a1d99b")
        .attr("stop-opacity", 1);
    gradient.append("svg:stop")
        .attr("offset", pSentimentValue(d).toString() + "%")
        .attr("stop-color", "#fc9272")
        .attr("stop-opacity", 1);
    return 'url(#' + gradientId(d) + '-gradient)';
  };
  resetGradientValue = function(d) {
    var svg = d3.select('svg#vis-main');
    var oldGradDef = d3.select('#' + gradientId(d)).remove();

    // Define the gradient
    gradient = svg.append("svg:defs")
        .attr("id", gradientId(d))
        .append("svg:linearGradient")
        .attr("id", gradientId(d) + "-gradient")
        .attr("x1", "0%")
        .attr("y1", "0%")
        .attr("x2", "100%")
        .attr("y2", "0%")
        .attr("spreadMethod", "pad");

    // Define the gradient colors
    gradient.append("svg:stop")
        .attr("offset", pSentimentValue(d).toString() + "%")
        .attr("stop-color", "#a1d99b")
        .attr("stop-opacity", 1);
    gradient.append("svg:stop")
        .attr("offset", pSentimentValue(d).toString() + "%")
        .attr("stop-color", "#fc9272")
        .attr("stop-opacity", 1);
    return 'url(#' + gradientId(d) + '-gradient)';
  };
  updateActiveGradient = function(d) {
    var svg = d3.select('svg#vis-main');
    var oldGradDef = d3.select('#' + gradientId(d)).remove();

    // Define the gradient
    gradient = svg.append("svg:defs")
        .attr("id", gradientId(d))
        .append("svg:linearGradient")
        .attr("id", gradientId(d) + "-gradient")
        .attr("x1", "0%")
        .attr("y1", "0%")
        .attr("x2", "100%")
        .attr("y2", "0%")
        .attr("spreadMethod", "pad");

    // Define the gradient colors
    gradient.append("svg:stop")
        .attr("offset", pSentimentValue(d).toString() + "%")
        .attr("stop-color", "#31a354")
        .attr("stop-opacity", 1);
    gradient.append("svg:stop")
        .attr("offset", pSentimentValue(d).toString() + "%")
        .attr("stop-color", "#de2d26")
        .attr("stop-opacity", 1);
    return 'url(#' + gradientId(d) + '-gradient)';
  };
  xStartValue = function(d) {
    return d.positiveProbability;
  };
  textValue = function(d) {
    return d.word;
  };
  collisionPadding = 4;
  minCollisionRadius = 12;
  jitter = 0.2;
  transformData = function(rawData) {
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
  tick = function(e) {
    var dampenedAlpha;
    dampenedAlpha = e.alpha * 0.15;
    // node.attr("cx", function(d) { return d.x = Math.max(rValue(d) / 4, Math.min(width, d.x)); }) .attr("cy", function(d) { return d.y = Math.max(rValue(d), Math.min(height - rValue(d), d.y)); });
    node.each(gravity(dampenedAlpha)).each(collide(jitter)).attr("transform", function(d) {
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
  chart = function(selection) {
    return selection.each(function(rawData) {
      var maxDomainValue, svg, svgEnter;
      data = transformData(rawData);
      maxDomainValue = d3.max(data, function(d) {
        return rValue(d);
      });
      rScale.domain([0, maxDomainValue]);
      svg = d3.select(this).selectAll("svg").data([data]);
      svgEnter = svg.enter().append("svg");
      svg.attr("width", width );//+ margin.left + margin.right);
      svg.attr("height", height + margin.top + margin.bottom);
      svg.attr("id", "vis-main");
      // svg.append("svg:defs").attr("id", "sentiment-gradients");
      node = svgEnter.append("g").attr("id", "bubble-nodes").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
      node.append("rect").attr("id", "bubble-background").on("click", clear);
      label = d3.select(this).selectAll("#bubble-labels").data([data]).enter().append("div").attr("id", "bubble-labels");
      update();
      hashchange();
      return d3.select(window).on("hashchange", hashchange);
    });
  };
  update = function() {
    data.forEach(function(d, i) {
      return d.forceR = Math.max(minCollisionRadius, rScale(rValue(d)));
    });
    force.nodes(data).start();
    updateNodes();
    return updateLabels();
  };
  updateNodes = function() {
    node = node.selectAll(".bubble-node").data(data, function(d) {
      return idValue(d);
    });
    node.exit().remove();
    return node.enter().append("a").attr("class", "bubble-node").attr("xlink:href", function(d) {
      return "#" + (encodeURIComponent(idValue(d)));
    }).call(force.drag).call(connectEvents).append("circle").attr("r", function(d) {
      return rScale(rValue(d));
    })
    // Fill the circle with the gradient
    .attr('fill', function(d) {
      return createGradientValue(d);
    });
  };
  updateLabels = function() {
    var labelEnter;
    label = label.selectAll(".bubble-label").data(data, function(d) {
      return idValue(d);
    });
    label.exit().remove();
    labelEnter = label.enter().append("a").attr("class", "bubble-label").attr("href", function(d) {
      return "#" + (encodeURIComponent(idValue(d)));
    }).call(force.drag).call(connectEvents);
    labelEnter.append("div").attr("class", "bubble-label-name").text(function(d) {
      return textValue(d);
    });
    labelEnter.append("div").attr("class", "bubble-label-value").text(function(d) {
      return rValue(d);
    });
    label.style("font-size", function(d) {
      return Math.max(8, rScale(rValue(d) / 3.5)) + "px";
    }).style("width", function(d) {
      return 2.5 * rScale(rValue(d)) + "px";
    });
    label.append("span").text(function(d) {
      return textValue(d);
    }).each(function(d) {
      return d.dx = Math.max(2.5 * rScale(rValue(d)), this.getBoundingClientRect().width);
    }).remove();
    label.style("width", function(d) {
      return d.dx + "px";
    });
    return label.each(function(d) {
      return d.dy = this.getBoundingClientRect().height;
    });
  };
  gravity = function(alpha) {
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
  collide = function(jitter) {
    return function(d) {
      return data.forEach(function(d2) {
        var distance, minDistance, moveX, moveY, x, y;
        if (d !== d2) {
          x = d.x - d2.x;
          y = d.y - d2.y;
          distance = Math.sqrt(x * x + y * y);
          minDistance = d.forceR + d2.forceR + collisionPadding;
          if (distance < minDistance) {
            distance = (distance - minDistance) / distance * jitter;
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
  connectEvents = function(d) {
    d.on("click", click);
    d.on("mouseover", mouseover);
    return d.on("mouseout", mouseout);
  };
  clear = function() {
    return location.replace("#");
  };
  click = function(d) {
    location.replace("#" + encodeURIComponent(idValue(d)));
    return d3.event.preventDefault();
  };
    hashchange = function() {
    var id;
    id = decodeURIComponent(location.hash.substring(1)).trim();
    return updateActive(id);
  };
  updateActive = function(id) {
    // Set the new active gradient
    var currentNode;
    d3.selectAll(".bubble-node").attr('fill', function(d) {
      if (idValue(d) == id) {
        currentNode = d;
        return updateActiveGradient(d);
      } else {
        return resetGradientValue(d);
      };
    });
    node.classed("bubble-selected", function(d) {
      return id === idValue(d);
    });
    if (id.length > 0) {
      showReviews(currentNode, id)
    }
  };
  showReviews = function(currentNode, id) {

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
				 //var row = findElement(data1.rows, "id" , item.review_id)
				 //alert(row);
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
    
  	tooltip.text("positive : " + pSentimentValue(d)+"%  negative : " + nSentimentValue(d)+"%");
	tooltip.style("visibility", "visible");
    return node.classed("bubble-hover", function(p) {
      return p === d;
    });
  };
  mouseout = function(d) {
  tooltip.style("visibility", "hidden")
    return node.classed("bubble-hover", false);
  };
  function findElement(arr, propName, propValue) {
  for (var i=0; i < arr.length; i++)
  {
    if (arr[i][propName] == propValue)
      return arr[i];
      }
}
  chart.jitter = function(_) {
    if (!arguments.length) {
      return jitter;
    }
    jitter = _;
    force.start();
    return chart;
  };
  chart.height = function(_) {
    if (!arguments.length) {
      return height;
    }
    height = _;
    return chart;
  };
  chart.width = function(_) {
    if (!arguments.length) {
      return width;
    }
    width = _;
    return chart;
  };
  chart.r = function(_) {
    if (!arguments.length) {
      return rValue;
    }
    rValue = _;
    return chart;
  };
  return chart;
};

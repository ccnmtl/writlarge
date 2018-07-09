/* global d3: true */
/* exported FamilyNetworkVue */

var FamilyNetworkVue = {
    props: ['siteid'],
    template: '#family-network',
    data: function() {
        return {
            networkName: 'the-network',
            site: null,
            complete: false,
            iconSize: 24,
            patterns: {},
            nodes: [],
            edges: [],
            width: 0,
            height: 300
        };
    },
    methods: {
        getLineStyle: function(node) {
            if (node.relationship === 'associate') {
                return ('3, 3');
            } else {
                return 'solid';
            }
        },
        getRadius: function(node) {
            return this.iconSize / 2;
        },
        getNodeImage: function(group) {
            return WritLarge.staticUrl + 'png/pin-' + group + '.png';
        },
        getXPosition: function(node, center) {
            if (node.relationship === 'self') {
                return center;
            } else if (node.relationship === 'associate') {
                const max = this.width;
                const min = 0;
                return Math.random() * (max - min) + min;
            } else if (node.relationship === 'antecedent') {
                return center / 4;
            } else {
                return center + center / 2;
            }
        },
        getYPosition: function(node, height) {
            if (node.relationship === 'self') {
                return this.height / 3;
            } else if (node.relationship === 'associate') {
                const min = this.height / 2;
                const max = this.height;
                return Math.random() * (max - min) + min;
            } else {
                const min = this.height / 8;
                const max = this.height - this.height / 4;
                return Math.random() * (max - min) + min;
            }
        },
        positionLabelX: function(node) {
            if (node.relationship === 'self' ||
                    node.relationship === 'associate') {
                // roughly center
                return -node.title.length * 7 / 2;
            } else if (node.relationship === 'antecedent') {
                return -node.title.length * 9;
            } else if (node.relationship === 'descendant') {
                return 15;
            }
        },
        positionLabelY: function(node) {
            if (node.relationship === 'self') {
                return -20;
            } else if (node.relationship === 'associate') {
                return 25;
            } else if (node.relationship === 'antecedent') {
                return 5;
            } else if (node.relationship === 'descendant') {
                return 5;
            }
        },
        clearDiagram: function() {
            if (this.simulation) {
                d3.select('svg').selectAll('*').remove();
                this.simulation.nodes(this.nodes).on('tick', null);
                delete this.simulation;
            }
        },
        createPatterns: function(svg) {
            let defs = svg.append('svg:defs');
            for (let group in this.patterns) {
                if (this.patterns.hasOwnProperty(group)) {
                    defs.append('svg:pattern')
                        .attr('id', group)
                        .attr('height','100%')
                        .attr('width', '100%')
                        .append('svg:image')
                        .attr('xlink:href', this.patterns[group])
                        .attr('width', this.iconSize)
                        .attr('height', this.iconSize)
                        .attr('x', 0)
                        .attr('y', 0);
                }
            }
        },
        boxForce: function() {
            const radius = this.iconSize / 2;
            for (var i = 0; i < this.nodes.length; ++i) {
                const node = this.nodes[i];
                node.x = Math.max(this.iconSize / 2,
                    Math.min(this.width - radius, node.x));
                node.y = Math.max(this.iconSize / 2,
                    Math.min(this.height - radius, node.y));
            }
        },
        buildDiagram: function() {
            if (this.nodes.length <= 1) {
                return;
            }

            const self = this;
            this.clearDiagram();

            const elt = document.getElementById(this.networkName);
            this.width = elt.clientWidth;
            const center = this.width / 2;

            let svg = d3.select('svg');
            svg.attr('width', this.width).attr('height', this.height);

            this.createPatterns(svg);

            const linkForce = d3
                .forceLink()
                .id(function(link) { return link.id; })
                .strength(function(link) { return .05; });

            this.simulation = d3
                .forceSimulation(this.nodes)
                .force('link', linkForce)
                .force('box_force', this.boxForce)
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(center, this.height / 2))
                .force('y', d3.forceY().y(function(d) {
                    return self.getYPosition(d, this.height);
                }))
                .force('x', d3.forceX().x(function(d) {
                    return self.getXPosition(d, center);
                }))
                .force('collision', d3.forceCollide().radius(function(d) {
                    return this.iconSize * 5;
                }));

            const linkElements = svg.append('g')
                .attr('class', 'links')
                .selectAll('line')
                .data(this.edges)
                .enter().append('line')
                .attr('stroke-width', 1)
                .attr('stroke', 'rgba(50, 50, 50, 0.5)')
                .style('stroke-dasharray', this.getLineStyle);

            /* eslint-disable scanjs-rules/assign_to_href */
            const nodeElements = svg.append('g')
                .attr('class', 'nodes')
                .selectAll('circle')
                .data(this.nodes)
                .enter().append('circle')
                .attr('r', this.getRadius)
                .style('fill', function(node) {
                    return 'url(#' + node.group + ')';
                })
                .on('click', function(d) {
                    location.href = '/view/' + d.id + '/';
                });
            /* eslint-enable scanjs-rules/assign_to_href */

            const textElements = svg.append('g')
                .attr('class', 'texts')
                .selectAll('text')
                .data(this.nodes)
                .enter().append('text')
                .text(function(node) { return node.title; })
                .attr('font-size', 15)
                .attr('dx', this.positionLabelX)
                .attr('dy', this.positionLabelY);

            this.simulation.nodes(this.nodes).on('tick', function(node) {
                nodeElements
                    .attr('cx', function(node) { return node.x; })
                    .attr('cy', function(node) { return node.y; });
                textElements
                    .attr('x', function(node) { return node.x; })
                    .attr('y', function(node) { return node.y; });
                linkElements
                    .attr('x1', function(link) { return link.source.x; })
                    .attr('y1', function(link) { return link.source.y; })
                    .attr('x2', function(link) { return link.target.x; })
                    .attr('y2', function(link) { return link.target.y; });
            });

            this.simulation.force('link').links(this.edges);
        }
    },
    created: function() {
        const url = WritLarge.baseUrl + 'api/site/' +  this.siteid + '/';
        jQuery.getJSON(url, (data) => {
            this.nodes = data.family;
            this.nodes.unshift({
                'id': data.id,
                'title': data.title,
                'group': data.category[0].group,
                'relationship': 'self'
            });
            for (let node of this.nodes) {
                const group = node.group;
                if (!(group in this.patterns)) {
                    this.patterns[group] = this.getNodeImage(group);
                }

                if (node.relationship !== 'self') {
                    this.edges.push({
                        source: data.id,
                        target: node.id,
                        relationship: node.relationship
                    });
                }
            }
            this.site = data;
        });
    },
    mounted: function() {
        // eslint-disable-next-line scanjs-rules/call_addEventListener
        window.addEventListener('resize', this.buildDiagram);
    },
    updated: function() {
        this.buildDiagram();
    }
};

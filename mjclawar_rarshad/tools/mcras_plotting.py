"""
File: mcras_plotting.py

Description: Plotting functions for mjclawar_rarshad (mcras)
Author(s): Raaid Arshad and Michael Clawar

Notes:
"""

import numpy as np
import mplleaflet

import matplotlib.pyplot as plt


class MCRASPlotting:
    @staticmethod
    def leaflet_heatmap(yy, xx, Z, bounds, tiles='cartodb_positron',
                        map_path='_map.html', legend_text=''):
        """
        Plots a heatmap over a leaflet layer
        Parameters
        ----------
        yy: np.array of y-coordinates
        xx: np.array of x-coordinates
        Z: np.array of Z-coordinates
        bounds: ((x_min, y_min), (x_max, y_max)) or None
        tiles: str
            Name of the tiles to use
        map_path: str
            Where to output html
        legend_text: str
            Text to put on the legend
        Returns
        -------

        """

        plt.figure()
        plt.pcolormesh(yy, xx, Z, cmap='YlGnBu', alpha=2)
        plt.xlim(bounds[0][0], bounds[1][0])
        plt.ylim(bounds[0][1], bounds[1][1])

        html = mplleaflet.fig_to_html(tiles='cartodb_positron')

        vmin = Z.min()
        vmax = Z.max()
        mplleaflet.save_html(fileobj=map_path, tiles=tiles)
        html_out = ''

        # Terrible but effective way to get around limitations of mplleaflet's lack of legend
        with open(map_path, 'r') as f:
            for line in f:
                if line.strip() == '<head>':
                    html_out +='<head>'
                    html_out += '<style> .caption {font-size: 150%; font-family:Arimo;}</style>'
                    html_out += '<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js">' \
                                '</script>\n'
                    continue
                if line.strip() == '</script>':
                    break
                if 'map' in line:
                    if 'map.org' in line:
                        html_out += line.replace('(map)', '(mymap)')
                        continue
                    line = line.replace('var map', 'var mymap').replace('(map)', '(mymap)').\
                        replace('map.fitBounds', 'mymap.fitBounds').replace('map.setView', 'mymap.setView')
                html_out += line.replace('"opacity": 1', '"opacity": 1, "fillOpacity": 0.65')

        html_out += '\n'
        html_out += 'var color_map = {};\n'
        html_out += 'color_map.color = d3.scale.threshold().domain(%s).range(["#f2f9bc", "#DCF1B2", "#bbe4b5", ' \
                    '"#84CFBA", "#57BEC0", "#34A8C2", "#1D8CBE", "#2166AB", "#23469C", "1C2D83"])\n' % \
                    str(list(np.linspace(vmin, vmax, 10)))
        html_out += 'color_map.x = d3.scale.linear().domain(%s).range([0, 400]);\n' % str([vmin, vmax])

        html_out += 'color_map.legend = L.control({position: "topright"});\n'
        html_out += 'color_map.legend.onAdd = function (map) {var div = L.DomUtil.create("div", "legend"); ' \
                    'return div};\n'
        html_out += 'color_map.legend.addTo(mymap);\n'

        html_out += 'color_map.xAxis = d3.svg.axis().scale(color_map.x).orient("top").' + \
                    'tickSize(1).tickValues(%s);\n' % str(list(np.linspace(vmin, vmax, 10)))
        html_out += 'color_map.svg = d3.select(".legend.leaflet-control").append("svg").attr("id", "legend")' \
                    '.attr("width", 450).attr("height", 50).style("background-color", "white");\n'
        html_out += 'color_map.g = color_map.svg.append("g").attr("class", "key").attr("transform", ' \
                    '"translate(25,16)");\n'
        html_out += 'color_map.g.selectAll("rect")\n'
        html_out += '.data(color_map.color.range().map(function(d, i) {\n'
        html_out += 'return {\n'
        html_out += 'x0: i ? color_map.x(color_map.color.domain()[i - 1]) : color_map.x.range()[0],\n'
        html_out += 'x1: i < color_map.color.domain().length ? color_map.x(color_map.color.domain()[i]) : ' \
                    'color_map.x.range()[1],\n'
        html_out += 'z: d\n'
        html_out += '};\n'
        html_out += '}))\n'
        html_out += '.enter().append("rect")\n'
        html_out += '.attr("height", 10)\n'
        html_out += '.attr("x", function(d) { return d.x0; })\n'
        html_out += '.attr("width", function(d) { return d.x1 - d.x0; })\n'
        html_out += '.style("fill", function(d) { return d.z; });\n'

        html_out += 'color_map.g.call(color_map.xAxis).append("text")\n'
        html_out += '.attr("class", "caption")\n'
        html_out += '.attr("y", 30)\n'
        html_out += '.text("%s");\n' % legend_text
        html_out += '</script></body>'
        with open(map_path, 'w') as f:
            f.write(html_out)
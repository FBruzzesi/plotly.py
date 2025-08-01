# Test annotations added by calling hline, vline, hrect, vrect with the annotation* keywords
#
# How to use this test:
# Normally the test is run as part of the test suite for plotly.py run using
# pytest. To run this test, simply run pytest path/to/this/file.py
# Some tests compare a figure generated by this test with an expected figure
# stored in JSON format (somewhat like the plotly.js image tests). Actually only
# the annotations part of this figure is stored and compared. It could be that
# this figure needs to be updated from time to time. To update the figure, run
# (from an appropriate development environment)
#
#   (plotly.py/venv)% WRITE_JSON=1 python path/to/this/file.py
#
# This will generate a figure and write it to a file. See below in the code for
# where the file is written.
# To see what the generated figure looks like, you can run
#
#   (plotly.py/venv)% VISUALIZE=1 python path/to/this/file.py
#
# and the figure will be shown in your default browser.
# Note for the above commands python was used and not pytest. pytest should only
# be used when running the tests.

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from itertools import product
import os
import pytest
import json
from .common import _cmp_partial_dict


@pytest.fixture
def single_plot_fixture():
    fig = go.Figure()
    fig.update_xaxes(range=[0, 10])
    fig.update_yaxes(range=[0, 10])
    fig.add_trace(go.Scatter(x=[], y=[]))
    return fig


@pytest.fixture
def multi_plot_fixture():
    fig = make_subplots(2, 2)
    for r, c in product(range(2), range(2)):
        r += 1
        c += 1
        fig.update_xaxes(row=r, col=c, range=[0, 10])
        fig.update_yaxes(row=r, col=c, range=[0, 10])
        fig.add_trace(go.Scatter(x=[], y=[]), row=r, col=c)
    return fig


# Make sure adding a shape without specifying an annotation doesn't add any annotations
def test_add_shape_no_annotation(multi_plot_fixture):
    multi_plot_fixture.add_hline(y=2, row="all", col="all")
    assert len(multi_plot_fixture.layout.annotations) == 0
    assert len(multi_plot_fixture.layout.shapes) == 4


# Adding without row and column on single plot works.
def test_add_annotated_shape_single_plot(single_plot_fixture):
    single_plot_fixture.add_hline(y=1, annotation_text="A")
    single_plot_fixture.add_vline(x=2, annotation_text="B")
    single_plot_fixture.add_hrect(y0=3, y1=4, annotation_text="C")
    single_plot_fixture.add_vrect(x0=5, x1=6, annotation_text="D")
    ret = len(single_plot_fixture.layout.annotations) == 4
    for sh, d in zip(
        single_plot_fixture.layout.annotations,
        [{"text": "A"}, {"text": "B"}, {"text": "C"}, {"text": "D"}],
    ):
        ret &= _cmp_partial_dict(sh, d)
    assert ret


# Adding without row and column on multi-facted plot works.
def test_add_annotated_shape_multi_plot(multi_plot_fixture):
    multi_plot_fixture.add_hline(y=1, annotation_text="A")
    multi_plot_fixture.add_vline(x=2, annotation_text="B")
    multi_plot_fixture.add_hrect(y0=3, y1=4, annotation_text="C")
    multi_plot_fixture.add_vrect(x0=5, x1=6, annotation_text="D")
    ax_nums = ["", "2", "3", "4"]
    ret = len(multi_plot_fixture.layout.annotations) == 16
    for sh, d in zip(
        multi_plot_fixture.layout.annotations,
        [
            {"text": "A", "xref": "x%s domain" % (n,), "yref": "y%s" % (n,)}
            for n in ax_nums
        ]
        + [
            {"text": "B", "xref": "x%s" % (n,), "yref": "y%s domain" % (n,)}
            for n in ax_nums
        ]
        + [
            {"text": "C", "xref": "x%s domain" % (n,), "yref": "y%s" % (n,)}
            for n in ax_nums
        ]
        + [
            {"text": "D", "xref": "x%s" % (n,), "yref": "y%s domain" % (n,)}
            for n in ax_nums
        ],
    ):
        ret &= _cmp_partial_dict(sh, d)
    assert ret


# Test that supplying a bad annotation position throws an error
def test_bad_annotation_position(multi_plot_fixture):
    bad_pos = "russula delica"
    with pytest.raises(
        ValueError, match='Invalid annotation position "%s"' % (bad_pos,)
    ):
        multi_plot_fixture.add_vline(
            x=3, annotation_text="Bad position", annotation_position=bad_pos
        )


# Test that position descriptions can be given in arbitrary order
def test_position_order(multi_plot_fixture):
    multi_plot_fixture.add_hrect(
        y0=3,
        y1=6,
        row=1,
        col=2,
        annotation_text="Position order",
        annotation_position="left bottom outside",
    )
    ret = len(multi_plot_fixture.layout.annotations) == 1
    for sh, d in zip(
        multi_plot_fixture.layout.annotations,
        [
            dict(
                text="Position order",
                x=0,
                y=3,
                xanchor="left",
                yanchor="top",
                xref="x2 domain",
                yref="y2",
            )
        ],
    ):
        ret &= _cmp_partial_dict(sh, d)
    assert ret


# Test that you can override values computed from the annotation position.
def test_annotation_position_override(multi_plot_fixture):
    multi_plot_fixture.add_hline(
        row=2,
        col=2,
        y=1,
        annotation_text="A",
        annotation_position="top left",
        annotation_xanchor="center",
    )
    multi_plot_fixture.add_vline(
        row=1,
        col=2,
        x=2,
        annotation_text="B",
        annotation_position="bottom left",
        annotation_yanchor="middle",
    )
    multi_plot_fixture.add_hrect(
        row=2,
        col=1,
        y0=3,
        y1=5,
        annotation_text="C",
        annotation_position="outside left",
        annotation_xanchor="center",
    )
    multi_plot_fixture.add_vrect(
        row=1,
        col=1,
        x0=4,
        x1=6,
        annotation_text="D",
        annotation_position="inside bottom right",
        annotation_yanchor="middle",
        annotation_xanchor="center",
    )
    ret = len(multi_plot_fixture.layout.annotations) == 4
    for sh, d in zip(
        multi_plot_fixture.layout.annotations,
        [
            {
                "xanchor": "center",
                "xref": "x4 domain",
                "yref": "y4",
                "x": 0,
                "y": 1,
                "text": "A",
            },
            {
                "yanchor": "middle",
                "xref": "x2",
                "yref": "y2 domain",
                "x": 2,
                "y": 0,
                "text": "B",
            },
            {
                "xanchor": "center",
                "xref": "x3 domain",
                "yref": "y3",
                "x": 0,
                "y": 4,
                "text": "C",
            },
            {
                "xanchor": "center",
                "yanchor": "middle",
                "xref": "x",
                "yref": "y domain",
                "x": 6,
                "y": 0,
                "text": "D",
            },
        ],
    ):
        ret &= _cmp_partial_dict(sh, d)
    assert ret


# Test that you can add an annotation using annotation=go.layout.Annotation(...)
def test_specify_annotation_as_Annotation(multi_plot_fixture):
    multi_plot_fixture.add_vrect(
        row=2,
        col=2,
        x0=2,
        x1=9,
        annotation=go.layout.Annotation(text="A", x=5.5, xanchor="center"),
        annotation_position="outside right",
    )
    ret = len(multi_plot_fixture.layout.annotations) == 1
    for sh, d in zip(
        multi_plot_fixture.layout.annotations,
        [
            {
                "text": "A",
                "x": 5.5,
                "xanchor": "center",
                "y": 0.5,
                "yanchor": "middle",
                "xref": "x4",
                "yref": "y4 domain",
            }
        ],
    ):
        ret &= _cmp_partial_dict(sh, d)
    assert ret


# Test that you can add an annotation using annotation=dict(...)
def test_specify_annotation_as_dict(multi_plot_fixture):
    multi_plot_fixture.add_vrect(
        row=2,
        col=2,
        x0=2,
        x1=9,
        annotation=dict(text="A", x=5.5, xanchor="center"),
        annotation_position="outside right",
    )
    ret = len(multi_plot_fixture.layout.annotations) == 1
    for sh, d in zip(
        multi_plot_fixture.layout.annotations,
        [
            {
                "text": "A",
                "x": 5.5,
                "xanchor": "center",
                "y": 0.5,
                "yanchor": "middle",
                "xref": "x4",
                "yref": "y4 domain",
            }
        ],
    ):
        ret &= _cmp_partial_dict(sh, d)
    assert ret


# Test the default and coerced positions work
def test_default_annotation_positions(multi_plot_fixture):
    # default position is (inside) top right
    multi_plot_fixture.add_hrect(row=2, col=2, y0=1, y1=8, annotation_text="A")
    multi_plot_fixture.add_vline(row=2, col=1, x=4, annotation_text="B")
    # if position on {h,v}rect lacks inside/outside specifier it defaults to inside
    multi_plot_fixture.add_vrect(
        row=1, col=2, x0=3, x1=6, annotation_text="C", annotation_position="bottom left"
    )
    ret = len(multi_plot_fixture.layout.annotations) == 3
    for sh, d in zip(
        multi_plot_fixture.layout.annotations,
        [
            {
                "text": "A",
                "x": 1,
                "y": 8,
                "xanchor": "right",
                "yanchor": "top",
                "xref": "x4 domain",
                "yref": "y4",
            },
            {
                "text": "B",
                "x": 4,
                "y": 1,
                "xanchor": "left",
                "yanchor": "top",
                "xref": "x3",
                "yref": "y3 domain",
            },
            {
                "text": "C",
                "x": 3,
                "y": 0,
                "xanchor": "left",
                "yanchor": "bottom",
                "xref": "x2",
                "yref": "y2 domain",
            },
        ],
    ):
        ret &= _cmp_partial_dict(sh, d)
    assert ret


def draw_all_annotation_positions(testing=False):
    visualize = os.environ.get("VISUALIZE", 0)
    write_json = os.environ.get("WRITE_JSON", 0)

    line_positions = [
        "top left",
        "top right",
        "top",
        "bottom left",
        "bottom right",
        "bottom",
        "left",
        "right",
    ]
    rect_positions = [
        "inside top left",
        "inside top right",
        "inside top",
        "inside bottom left",
        "inside bottom right",
        "inside bottom",
        "inside left",
        "inside right",
        "inside",
        "outside top left",
        "outside top right",
        "outside top",
        "outside bottom left",
        "outside bottom right",
        "outside bottom",
        "outside left",
        "outside right",
    ]
    fig = make_subplots(
        2, 2, column_widths=[3, 1], row_heights=[1, 3], vertical_spacing=0.07
    )
    for rc, pos, ax, sh in zip(
        product(range(2), range(2)),
        [line_positions, line_positions, rect_positions, rect_positions],
        ["x", "y", "x", "y"],
        ["vline", "hline", "vrect", "hrect"],
    ):
        r, c = rc
        r += 1
        c = ((c + 1) % 2 if r == 1 else c) + 1
        fig.update_xaxes(row=r, col=c, range=[0, len(pos) if sh[0] == "v" else 1])
        fig.update_yaxes(row=r, col=c, range=[0, len(pos) if sh[0] == "h" else 1])
        fig.add_trace(go.Scatter(x=[], y=[]), row=r, col=c)
        for n, p in enumerate(pos):
            f = eval("fig.add_%s" % (sh,))
            args = (
                {ax: n + 0.5}
                if sh.endswith("line")
                else {ax + "0": n + 0.1, ax + "1": n + 0.9}
            )
            args["annotation_text"] = p
            args["annotation_position"] = p
            args["annotation_font_size"] = 8
            args["annotation_font_color"] = "white"
            args["row"] = r
            args["col"] = c
            args["annotation_bgcolor"] = "grey"
            if sh[0] == "v":
                args["annotation_textangle"] = 90
            f(**args)
    fig.update_layout(title="Annotated hline, vline, hrect, vrect")

    # Get JSON representation of annotations
    annotations_json = json.dumps(
        json.loads(fig.to_json())["layout"]["annotations"], sort_keys=True
    )

    # compute path to where to write JSON annotations (this computes a path to a
    # file in the same directory as this test script)
    dirname0 = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(dirname0, "test_annotated_shapes_annotations.json")

    if (not testing) and write_json:
        # write the annotations
        with open(json_path, "w") as fd:
            fd.write(annotations_json)

    if (not testing) and visualize:
        fig.show()

    if testing:
        # check the generated json matches the loaded json
        with open(json_path, "r") as fd:
            loaded_annotations_json = fd.read()
            assert annotations_json == loaded_annotations_json


# Check all the annotations are in the expected positions
def test_all_annotation_positions():
    draw_all_annotation_positions(testing=True)


if __name__ == "__main__":
    draw_all_annotation_positions()

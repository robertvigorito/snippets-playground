"""Nuke execute rif operations.
"""
import os as _os
import logging as _logging
import dataclasses as _dataclasses

from typing import List as _List

# Package imports
import rifs as _rifs


_logger = _logging.getLogger("dd." + __name__)
_logger.addHandler(_logging.NullHandler())


FLAG_MAPPING = {
    "gpu": "--gpu",  #
    "render_order": "--sro",  # Force the application to obey the render order of Write nodes such that Reads can use files created by earlier Write nodes
    "interactive": "-i",  # with -x or -t use interactive, not render, license
    "proxy_mode": "-p",  # turn on proxy mode (use -f to force full size)
    "full_size": "-f",  # render at full size (turns off proxy; use -p to force render at proxy)
    "not_writes": "--rendertonull",  # Direct all writes to null when executing a script
    "classic_rendering": "--classic_rendering",  # Classic rendering architecture which renders the node graph scanline-by-scanline, on demand.
    "topdown": "--topdown",  # Top-down mode renders the node graph from the top to the bottom, node-by-node. It is faster than classic rendering, although it will consume more memory and lose progressive rendering. In cases where memory pressure is a high concern, or where progressive rendering is required, classic mode should be used.
}


@_dataclasses.dataclass(eq=True, order=True)
class NukeOperation(_rifs.core.ProcessorRif):
    """The operation constructs the Nuke race commandline arguments. Which allows
    us to successfully render a nuke script on the farm.

    Attributes:
        script (str): The path to the nuke script to render.
        nodes (List[str]): A list of node names to render.
        frange (str): The frame range to render. Accepts:
                      'A'        single frame number A
                      'A-B'      all frames from A through B
                      'A-BxC'    every C'th frame from A to last one less or equal to B
        gpu (bool): Enable GPU usage when in terminal mode with an optional gpu index argument, defaults to 0 if none given. Will override preferences when in interactive mode.
        render_order (bool): Force the application to obey the render order of Write nodes such that Reads can use files created by earlier Write nodes.
        interactive (bool): With -x or -t use interactive, not render, license.
        proxy_mode (bool): Turn on proxy mode (use -f to force full size).
        full_size (bool): Render at full size (turns off proxy; use -p to force render at proxy).
        not_writes (bool): Direct all writes to null when executing a script.
        classic_rendering (bool): Classic rendering architecture which renders the node graph scanline-by-scanline, on demand.
        topdown (bool): Top-down mode renders the node graph from the top to the bottom, node-by-node. It is faster than classic rendering, although it will consume more memory and lose progressive rendering. In cases where memory pressure is a high concern, or where progressive rendering is required, classic mode should be used.
        

    Examples:
        >>> nuke_render = NukeOperation(
        ...     script="/dd/shows/BIMINI/RD/1212/user/work.rvigorito/nuke/comp/rd1212_comp_v001.nk",
        ...     frange="1009-1184",
        ...     nodes=["DDWrite.Write"]
        ... )
        >>> nuke_render()

    """

    script: str = _dataclasses.field(default_factory=str)
    nodes: _List[str] = _dataclasses.field(default_factory=list)
    frange: str = _dataclasses.field(default_factory=str)

    # # Optional
    gpu: bool = _dataclasses.field(default=False)
    render_order: bool = _dataclasses.field(default=False, repr=False)
    interactive: bool = _dataclasses.field(default=False, repr=False)
    proxy_mode: bool = _dataclasses.field(default=False, repr=False)
    full_size: bool = _dataclasses.field(default=False, repr=False)
    not_writes: bool = _dataclasses.field(default=False, repr=False)
    classic_rendering: bool = _dataclasses.field(default=False)
    topdown: bool = _dataclasses.field(default=False)

    command: _List[str] = _dataclasses.field(default_factory=lambda: ["nuke-race", "-t", "-x"], init=False)

    def __post_init__(self):
        self.script = str(self.script)  # Ensure the script is a string
        self.notes = f"Nuke | {_os.path.basename(self.script)} | {self.frange} | {self.notes or 'NA'}"
        self.soumission_kwargs["outputImage"] = self.script
        self.soumission_kwargs["frame_range"] = self.frange
        self.build_command()

    def build_command(self) -> bool:
        """Build the nuke command from the object attributes.

        Returns:
            bool: True if the command was successfully built.
        """
        # Mapping the flags to the command if enabled
        for key in _dataclasses.asdict(self):
            if key in FLAG_MAPPING and getattr(self, key):
                self.command.append(FLAG_MAPPING[key])

        # Set the script frange and nodes execution
        if self.frange:
            self.command.extend(["-F", self.frange])
        if self.nodes:
            self.command.remove("-x")
            self.command.extend(["-X", ",".join(self.nodes)])
        self.command.extend(["--", self.script])
        return True

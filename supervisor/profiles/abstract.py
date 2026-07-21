from abc import ABC

from supervisor.norms.abstract import AbstractConstraint, AbstractNorm

class AbstractNormProfile(ABC):
    """Abstract class for norm profiles."""    
    def __init__(
        self,
        constraints: list[AbstractConstraint],
        norms: list[AbstractNorm]
    ):
        """Initialize the norm profile with hard constraints and norms.

        :param constraints: list of hard constraints
        :param norms: list of soft norms
        """
        self.constraints = constraints
        self.norms       = norms

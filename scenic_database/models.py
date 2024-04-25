from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

# Create an engine to connect to the database
engine = create_engine('sqlite:///scenario_database.db', echo=True)

# Create a base class for declarative class definitions
Base = declarative_base()

class FunctionalNominalScenario(Base):
    __tablename__ = "functional_nominal_scenarios"
    
    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True, nullable=False)

    # One-to-one relationship with TCEnhancedFunctionalScenario
    tc_enhanced_functional_scenario = relationship("TCEnhancedFunctionalScenario", uselist=False, back_populates="functional_nominal_scenario")

    # One-to-many relationship with LogicalNominalScenario
    logical_nominal_scenario_items = relationship("LogicalNominalScenario", back_populates="functional_nominal_scenario_item")

class LogicalNominalScenario(Base):
    __tablename__ = "logical_nominal_scenarios"

    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True, nullable=False)
    functional_nominal_scenario_id = Column(Integer, ForeignKey('functional_nominal_scenarios.id'))
    
    # One-to-one relationship with TCEnhancedLogicalScenario
    tc_enhanced_logical_scenario = relationship("TCEnhancedLogicalScenario", uselist=False, back_populates="logical_nominal_scenario")

    # Many-to-one relationship with FunctionalNominalScenario
    functional_nominal_scenario_item = relationship("FunctionalNominalScenario", back_populates="logical_nominal_scenario_items")
    # One-to-many relationship with ConcreteNominalScenario
    concrete_nominal_scenario_items = relationship("ConcreteNominalScenario", back_populates="logical_nominal_scenario_item")

class ConcreteNominalScenario(Base):
    __tablename__ = "concrete_nominal_scenarios"

    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True, nullable=False)
    logical_nominal_scenario_id = Column(Integer, ForeignKey('logical_nominal_scenarios.id'))

    # One-to-many relationship with TCEnhancedConcreteScenario
    tc_enhanced_concrete_scenario_items = relationship("TCEnhancedConcreteScenario", back_populates="concrete_nominal_scenario_item")

    # Many-to-one relationship with LogicalNominalScenario
    logical_nominal_scenario_item = relationship("LogicalNominalScenario", back_populates="concrete_nominal_scenario_items")

class TriggeringCondition(Base):
    __tablename__ = "triggering_conditions"

    id = Column(Integer, primary_key=True)
    triggering_condition_name = Column(String,  unique=True, nullable=False)
    functional_insufficiency = Column(String)
    functional_insufficiency_origin = Column(String)

    # One-to-many relationship with TCEnhancedFunctionalScenario
    tc_enhanced_functional_scenario_items = relationship("TCEnhancedFunctionalScenario", back_populates="triggering_condition_item")

class TCEnhancedFunctionalScenario(Base):
    __tablename__ = "tc_enhanced_functional_scenarios"

    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True, nullable=False)
    exist_non_complient = Column(Boolean, nullable=False)

    # One-to-one relationship with FunctionalNominalScenario
    functional_nominal_scenario_id = Column(Integer, ForeignKey('functional_nominal_scenarios.id'))
    functional_nominal_scenario = relationship("FunctionalNominalScenario", back_populates="tc_enhanced_functional_scenario")

    # Many-to-one relationship with LogicalNominalScenario
    triggering_condition_id = Column(Integer, ForeignKey('triggering_conditions.id'))
    triggering_condition_item = relationship("TriggeringCondition", back_populates="tc_enhanced_functional_scenario_items")
    # One-to-many relationship with TCEnhancedLogicalScenario
    tc_enhanced_logical_scenario_items = relationship("TCEnhancedLogicalScenario", back_populates="tc_enhanced_functional_scenario_item")
    
class TCEnhancedLogicalScenario(Base):
    __tablename__ = "tc_enhanced_logical_scenarios"

    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True, nullable=False)

    # One-to-one relationship with FunctionalNominalScenario
    logical_nominal_scenario_id = Column(Integer, ForeignKey('logical_nominal_scenarios.id'))
    logical_nominal_scenario = relationship("LogicalNominalScenario", back_populates="tc_enhanced_logical_scenario")

    # Many-to-one relationship with TCEnhancedFunctionalScenario
    tc_enhanced_functional_scenario_id = Column(Integer, ForeignKey('tc_enhanced_functional_scenarios.id'))
    tc_enhanced_functional_scenario_item = relationship("TCEnhancedFunctionalScenario", back_populates="tc_enhanced_logical_scenario_items")
    # One-to-many relationship with TCEnhancedConcreteScenario
    tc_enhanced_concrete_scenario_items = relationship("TCEnhancedConcreteScenario", back_populates="tc_enhanced_logical_scenario_item")

class TCEnhancedConcreteScenario(Base):
    __tablename__ = "tc_enhanced_concrete_scenarios"
    
    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True, nullable=False)

    # Many-to-one relationship with ConcreteNominalScenario
    concrete_nominal_scenario_id = Column(Integer, ForeignKey('concrete_nominal_scenarios.id'))
    concrete_nominal_scenario_item = relationship("ConcreteNominalScenario", back_populates="tc_enhanced_concrete_scenario_items")
    
    # Many-to-one relationship with TCEnhancedLogicalScenario
    tc_enhanced_logical_scenario_id = Column(Integer, ForeignKey('tc_enhanced_logical_scenarios.id'))
    tc_enhanced_logical_scenario_item = relationship("TCEnhancedLogicalScenario", back_populates="tc_enhanced_concrete_scenario_items")
    # One-to-one relationship with TestCase
    test_case = relationship("TestCase", back_populates="tc_enhanced_concrete_scenario", uselist=False)

    # 

class RequiredBehavior(Base):
    __tablename__ = "required_behaviors"

    id = Column(Integer, primary_key=True)
    behavior_name = Column(String,  unique=True, nullable=False)

    # One-to-one relationship with HazardousBehavior
    hazardous_behavior = relationship("HazardousBehavior", back_populates="required_behavior", uselist=False)

    # Many-to-many relationship with TestCase
    test_cases = relationship("TestCase", secondary="test_cases_required_behaviors", back_populates="required_behaviors")

class HazardousBehavior(Base):
    __tablename__ = "hazardous_behaviors"

    id = Column(Integer, primary_key=True)
    behavior_description = Column(String,  unique=True, nullable=False)
    
    # One-to-one relationship with RequiredBehavior
    required_behavior_id = Column(Integer, ForeignKey('required_behaviors.id'))
    required_behavior = relationship("RequiredBehavior", back_populates="hazardous_behavior")
    
    # Many-to-many relationship with TestCase
    test_results = relationship("TestResult", secondary="test_results_hazardous_behaviors", back_populates="hazardous_behaviors")

# Association table between TestCase and RequiredBehavior
class TestCaseRequiredBehavior(Base):
    __tablename__ = 'test_cases_required_behaviors'
    id = Column(Integer, primary_key=True)
    test_case_id = Column('test_case_id', Integer, ForeignKey('test_cases.id'))
    required_behavior_id = Column('required_behavior_id', Integer, ForeignKey('required_behaviors.id'))

class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True)

    # One-to-one relationship with TCEnhancedConcreteScenario
    tc_enhanced_concrete_scenario_id = Column(Integer, ForeignKey('tc_enhanced_concrete_scenarios.id'))
    tc_enhanced_concrete_scenario = relationship("TCEnhancedConcreteScenario", back_populates="test_case")

    # Many-to-many relationship with RequiredBehavior
    required_behaviors = relationship("RequiredBehavior", secondary="test_cases_required_behaviors", back_populates="test_cases")

    # One-to-many relationship with TestResult
    test_result_items = relationship("TestResult", back_populates="test_case_item")

# Association table between TestResult and HazardousBehavior
class TestResultHazardousBehavior(Base):
    __tablename__ = 'test_results_hazardous_behaviors'
    id = Column(Integer, primary_key=True)
    test_result_id = Column('test_result_id', Integer, ForeignKey('test_results.id'))
    hazardous_behavior_id = Column('hazardous_behavior_id', Integer, ForeignKey('hazardous_behaviors.id'))

class TestResult(Base):
    __tablename__ = 'test_results'

    id = Column(Integer, primary_key=True)
    system_info = Column(String, nullable=False)
    test_result = Column(Boolean, nullable=False)
    testing_date = Column(String, nullable=False)
    log_file = Column(String, nullable=False)
    # Many-to-one relationship with TestCase
    test_case_id = Column(Integer, ForeignKey('test_cases.id'))
    test_case_item = relationship("TestCase", back_populates="test_result_items")
    
    # Many-to-many relationship with HazardousBehavior
    hazardous_behaviors = relationship("HazardousBehavior", secondary="test_results_hazardous_behaviors", back_populates="test_results")



# Create the tables in the database
# Base.metadata.create_all(engine)

# # Create a session
# Session = sessionmaker(bind=engine)
# session = Session()

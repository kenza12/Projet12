from models.contract import Contract
import sentry_sdk
from utils.token_manager import TokenManager
from utils.session_manager import get_session


class ContractController:
    @staticmethod
    def get_all_contracts(token: str) -> list:
        """
        Retrieves all contracts if the user is authenticated and authorized.
        Args:
            token (str): JWT token of the authenticated user.
        Returns:
            list: List of Contract objects.
        """
        try:
            key = TokenManager.load_key()
            payload = TokenManager.verify_token(token, key)
            if payload:
                session = get_session()
                contracts = session.query(Contract).all()
                return contracts
            return []
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return []

    @staticmethod
    def get_contract_by_id(contract_id: int):
        """
        Retrieves a contract by its ID.
        Args:
            contract_id (int): ID of the contract to retrieve.
        Returns:
            Contract: The contract object if found, otherwise None.
        """
        try:
            session = get_session()
            contract = session.query(Contract).filter_by(id=contract_id).first()
            return contract
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    @staticmethod
    def get_client_id_by_contract_id(contract_id: int) -> int:
        """
        Retrieve the client ID based on the contract ID.
        Args:
            contract_id (int): The ID of the contract.
        Returns:
            int: The ID of the client if found, otherwise None.
        """
        contract = ContractController.get_contract_by_id(contract_id)
        if contract:
            return contract.client_id
        return None

    @staticmethod
    def create_contract(
        client_id: int,
        commercial_contact_id: int,
        total_amount: float,
        amount_due: float,
        date_created: str,
        signed: bool,
    ) -> bool:
        """
        Creates a new contract if data is valid.
        """
        try:
            session = get_session()
            contract = Contract(
                client_id=client_id,
                commercial_contact_id=commercial_contact_id,
                total_amount=total_amount,
                amount_due=amount_due,
                date_created=date_created,
                signed=signed,
            )
            session.add(contract)
            session.commit()
            return True
        except ValueError as ve:
            sentry_sdk.capture_exception(ve)
            print(f"Validation Error: {ve}")
            return False
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error creating contract: {e}")
            return False

    @staticmethod
    def update_contract(
        contract_id: int,
        client_id: int = None,
        total_amount: float = None,
        amount_due: float = None,
        signed: bool = None,
    ) -> bool:
        """
        Updates an existing contract if data is valid.
        """
        try:
            session = get_session()
            contract = session.query(Contract).filter_by(id=contract_id).first()
            if not contract:
                raise ValueError("Contract not found.")

            if client_id:
                contract.client_id = client_id
            if total_amount:
                contract.total_amount = total_amount
            if amount_due:
                contract.amount_due = amount_due
            if signed is not None:
                contract.signed = signed

            session.commit()
            return True
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return False

    @staticmethod
    def get_filtered_contracts(filters: dict) -> list:
        """
        Retrieves contracts based on specified filters.
        Args:
            filters (dict): Dictionary of filters.
        Returns:
            list: List of Contract objects that match the filters.
        """
        try:
            session = get_session()
            query = session.query(Contract)
            if "signed" in filters:
                query = query.filter(Contract.signed == filters["signed"])
            if "unpaid" in filters:
                query = query.filter(Contract.amount_due > 0)
            return query.all()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return []

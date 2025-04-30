from unittest.mock import patch
import pytest


def test_atualizar_usuario_sucesso(client):
    with patch('app.Routes.user_routes.AuthService') as mock_auth, \
         patch('app.Routes.user_routes.UserService') as mock_user, \
         patch('app.Utils.jwt_utils.TokenService') as mock_token:
            
        # Configura mock
        mock_token.return_value.verificar_token.return_value = {"email": "teste@email.com", "firebase_uid": "test123"}
        mock_auth.return_value.obter_usuario_por_token.return_value = {"id": 1}
        mock_user.return_value.atualizar_usuario.return_value = ({"mensagem": "Dados atualizados"}, 200)
        
        
        # Simula request com token válido
        response = client.put(
            '/usuario/atualizar',
            json={"nome": "Novo Nome"},
            headers={"Authorization": "Bearer token_valido"}
        )
        
        
        assert response.status_code == 200
        assert response.json["mensagem"] == "Dados atualizados"
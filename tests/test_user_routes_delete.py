from unittest.mock import patch, MagicMock
from functools import wraps

def test_deletar_usuario_sucesso(client):
    with patch('app.Routes.user_routes.AuthService') as mock_auth, \
         patch('app.Routes.user_routes.UserService') as mock_user, \
         patch('app.Utils.jwt_utils.TokenService') as mock_token:
        
        # Configura mocks
        mock_token.return_value.verificar_token.return_value = {"email": "teste@email.com", "firebase_uid": "test123"}
        mock_auth.return_value.obter_usuario_por_token.return_value = {"id": 1}
        mock_user.deletar_usuario.return_value = ({"mensagem": "Usuário deletado com sucesso"}, 200)
        
        # Teste
        response = client.delete(
            '/usuario/deletar',
            headers={"Authorization": "Bearer token_valido"}
        )
        
        assert response.status_code == 200
        assert "mensagem" in response.json





def test_deletar_usuario_nao_autorizado(client):
    with patch('app.Utils.jwt_utils.TokenService') as mock_token:
        # Simula token inválido
        mock_token.return_value.verificar_token.side_effect = ValueError("Token expirado")
        
        response = client.delete(
            '/usuario/deletar',
            headers={"Authorization": "Bearer token_expirado"}
        )
        
        assert response.status_code == 401
        assert "Token expirado" in response.json.get("erro", "")
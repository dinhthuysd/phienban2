import api from './api';

class Web3Service {
  // ============ NETWORK & WALLET INFO ============
  
  async getSupportedNetworks() {
    const response = await api.get('/web3/networks');
    return response.data;
  }
  
  async getPlatformWallets() {
    const response = await api.get('/web3/platform-wallets');
    return response.data;
  }
  
  async getUserWallet() {
    const response = await api.get('/web3/wallet');
    return response.data;
  }
  
  // ============ DEPOSITS ============
  
  async submitCryptoDeposit(depositData) {
    const response = await api.post('/web3/deposit', depositData);
    return response.data;
  }
  
  async getCryptoDepositHistory() {
    const response = await api.get('/web3/deposit-history');
    return response.data;
  }
  
  // ============ WITHDRAWALS ============
  
  async submitCryptoWithdrawal(withdrawalData) {
    const response = await api.post('/web3/withdrawal', withdrawalData);
    return response.data;
  }
  
  async getCryptoWithdrawalHistory() {
    const response = await api.get('/web3/withdrawal-history');
    return response.data;
  }
  
  // ============ METAMASK INTEGRATION ============
  
  async connectMetaMask() {
    if (typeof window.ethereum === 'undefined') {
      throw new Error('MetaMask is not installed. Please install MetaMask extension.');
    }
    
    try {
      const accounts = await window.ethereum.request({ 
        method: 'eth_requestAccounts' 
      });
      
      return {
        address: accounts[0],
        connected: true
      };
    } catch (error) {
      if (error.code === 4001) {
        throw new Error('User rejected the connection request');
      }
      throw error;
    }
  }
  
  async getMetaMaskAccount() {
    if (typeof window.ethereum === 'undefined') {
      return null;
    }
    
    try {
      const accounts = await window.ethereum.request({ 
        method: 'eth_accounts' 
      });
      
      if (accounts.length > 0) {
        return accounts[0];
      }
      
      return null;
    } catch (error) {
      console.error('Error getting MetaMask account:', error);
      return null;
    }
  }
  
  async getMetaMaskBalance(address) {
    if (typeof window.ethereum === 'undefined') {
      throw new Error('MetaMask is not installed');
    }
    
    try {
      const balance = await window.ethereum.request({
        method: 'eth_getBalance',
        params: [address, 'latest']
      });
      
      // Convert from Wei to ETH
      const balanceInEth = parseInt(balance, 16) / 1e18;
      
      return balanceInEth;
    } catch (error) {
      console.error('Error getting balance:', error);
      throw error;
    }
  }
  
  async switchNetwork(chainId) {
    if (typeof window.ethereum === 'undefined') {
      throw new Error('MetaMask is not installed');
    }
    
    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: `0x${chainId.toString(16)}` }],
      });
    } catch (error) {
      // Chain doesn't exist, add it
      if (error.code === 4902) {
        await this.addNetwork(chainId);
      } else {
        throw error;
      }
    }
  }
  
  async addNetwork(chainId) {
    const networks = {
      1: {
        chainId: '0x1',
        chainName: 'Ethereum Mainnet',
        nativeCurrency: { name: 'Ether', symbol: 'ETH', decimals: 18 },
        rpcUrls: ['https://mainnet.infura.io/v3/'],
        blockExplorerUrls: ['https://etherscan.io']
      },
      56: {
        chainId: '0x38',
        chainName: 'Binance Smart Chain',
        nativeCurrency: { name: 'BNB', symbol: 'BNB', decimals: 18 },
        rpcUrls: ['https://bsc-dataseed.binance.org/'],
        blockExplorerUrls: ['https://bscscan.com']
      },
      137: {
        chainId: '0x89',
        chainName: 'Polygon Mainnet',
        nativeCurrency: { name: 'MATIC', symbol: 'MATIC', decimals: 18 },
        rpcUrls: ['https://polygon-rpc.com/'],
        blockExplorerUrls: ['https://polygonscan.com']
      },
      11155111: {
        chainId: '0xaa36a7',
        chainName: 'Sepolia Testnet',
        nativeCurrency: { name: 'Sepolia ETH', symbol: 'ETH', decimals: 18 },
        rpcUrls: ['https://sepolia.infura.io/v3/'],
        blockExplorerUrls: ['https://sepolia.etherscan.io']
      }
    };
    
    const networkConfig = networks[chainId];
    
    if (!networkConfig) {
      throw new Error('Network not supported');
    }
    
    await window.ethereum.request({
      method: 'wallet_addEthereumChain',
      params: [networkConfig],
    });
  }
  
  async getCurrentNetwork() {
    if (typeof window.ethereum === 'undefined') {
      return null;
    }
    
    try {
      const chainId = await window.ethereum.request({ 
        method: 'eth_chainId' 
      });
      
      return parseInt(chainId, 16);
    } catch (error) {
      console.error('Error getting network:', error);
      return null;
    }
  }
  
  // Listen for account changes
  onAccountsChanged(callback) {
    if (typeof window.ethereum !== 'undefined') {
      window.ethereum.on('accountsChanged', callback);
    }
  }
  
  // Listen for chain changes
  onChainChanged(callback) {
    if (typeof window.ethereum !== 'undefined') {
      window.ethereum.on('chainChanged', callback);
    }
  }
}

export default new Web3Service();

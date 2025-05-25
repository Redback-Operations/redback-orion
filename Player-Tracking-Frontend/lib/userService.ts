import fs from 'fs';
import path from 'path';

const usersFilePath = path.join(process.cwd(), 'data', 'users.json');

interface User {
  id: string;
  email: string;
  name: string;
  password: string;
}

export const userService = {
  getUsers: (): User[] => {
    if (!fs.existsSync(usersFilePath)) {
      fs.writeFileSync(usersFilePath, JSON.stringify({ users: [] }, null, 2));
    }
    const data = JSON.parse(fs.readFileSync(usersFilePath, 'utf8'));
    return data.users;
  },

  saveUser: (user: User) => {
    const data = { users: [...userService.getUsers(), user] };
    fs.writeFileSync(usersFilePath, JSON.stringify(data, null, 2));
    return user;
  },

  findUser: (email: string): User | undefined => {
    const users = userService.getUsers();
    return users.find(user => user.email === email);
  }
};
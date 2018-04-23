package conflerge.tree.visitor;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import com.github.javaparser.ast.ArrayCreationLevel;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.ImportDeclaration;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.PackageDeclaration;
import com.github.javaparser.ast.body.AnnotationDeclaration;
import com.github.javaparser.ast.body.AnnotationMemberDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.EmptyMemberDeclaration;
import com.github.javaparser.ast.body.EnumConstantDeclaration;
import com.github.javaparser.ast.body.EnumDeclaration;
import com.github.javaparser.ast.body.FieldDeclaration;
import com.github.javaparser.ast.body.InitializerDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.Parameter;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.comments.BlockComment;
import com.github.javaparser.ast.comments.Comment;
import com.github.javaparser.ast.comments.JavadocComment;
import com.github.javaparser.ast.comments.LineComment;
import com.github.javaparser.ast.expr.ArrayAccessExpr;
import com.github.javaparser.ast.expr.ArrayCreationExpr;
import com.github.javaparser.ast.expr.ArrayInitializerExpr;
import com.github.javaparser.ast.expr.AssignExpr;
import com.github.javaparser.ast.expr.BinaryExpr;
import com.github.javaparser.ast.expr.BooleanLiteralExpr;
import com.github.javaparser.ast.expr.CastExpr;
import com.github.javaparser.ast.expr.CharLiteralExpr;
import com.github.javaparser.ast.expr.ClassExpr;
import com.github.javaparser.ast.expr.ConditionalExpr;
import com.github.javaparser.ast.expr.DoubleLiteralExpr;
import com.github.javaparser.ast.expr.EnclosedExpr;
import com.github.javaparser.ast.expr.FieldAccessExpr;
import com.github.javaparser.ast.expr.InstanceOfExpr;
import com.github.javaparser.ast.expr.IntegerLiteralExpr;
import com.github.javaparser.ast.expr.LambdaExpr;
import com.github.javaparser.ast.expr.LongLiteralExpr;
import com.github.javaparser.ast.expr.MarkerAnnotationExpr;
import com.github.javaparser.ast.expr.MemberValuePair;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.expr.MethodReferenceExpr;
import com.github.javaparser.ast.expr.Name;
import com.github.javaparser.ast.expr.NameExpr;
import com.github.javaparser.ast.expr.NormalAnnotationExpr;
import com.github.javaparser.ast.expr.NullLiteralExpr;
import com.github.javaparser.ast.expr.ObjectCreationExpr;
import com.github.javaparser.ast.expr.SimpleName;
import com.github.javaparser.ast.expr.SingleMemberAnnotationExpr;
import com.github.javaparser.ast.expr.StringLiteralExpr;
import com.github.javaparser.ast.expr.SuperExpr;
import com.github.javaparser.ast.expr.ThisExpr;
import com.github.javaparser.ast.expr.TypeExpr;
import com.github.javaparser.ast.expr.UnaryExpr;
import com.github.javaparser.ast.expr.VariableDeclarationExpr;
import com.github.javaparser.ast.nodeTypes.NodeWithModifiers;
import com.github.javaparser.ast.stmt.AssertStmt;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.stmt.BreakStmt;
import com.github.javaparser.ast.stmt.CatchClause;
import com.github.javaparser.ast.stmt.ContinueStmt;
import com.github.javaparser.ast.stmt.DoStmt;
import com.github.javaparser.ast.stmt.EmptyStmt;
import com.github.javaparser.ast.stmt.ExplicitConstructorInvocationStmt;
import com.github.javaparser.ast.stmt.ExpressionStmt;
import com.github.javaparser.ast.stmt.ForStmt;
import com.github.javaparser.ast.stmt.ForeachStmt;
import com.github.javaparser.ast.stmt.IfStmt;
import com.github.javaparser.ast.stmt.LabeledStmt;
import com.github.javaparser.ast.stmt.LocalClassDeclarationStmt;
import com.github.javaparser.ast.stmt.ReturnStmt;
import com.github.javaparser.ast.stmt.SwitchEntryStmt;
import com.github.javaparser.ast.stmt.SwitchStmt;
import com.github.javaparser.ast.stmt.SynchronizedStmt;
import com.github.javaparser.ast.stmt.ThrowStmt;
import com.github.javaparser.ast.stmt.TryStmt;
import com.github.javaparser.ast.stmt.WhileStmt;
import com.github.javaparser.ast.type.ArrayType;
import com.github.javaparser.ast.type.ClassOrInterfaceType;
import com.github.javaparser.ast.type.IntersectionType;
import com.github.javaparser.ast.type.PrimitiveType;
import com.github.javaparser.ast.type.TypeParameter;
import com.github.javaparser.ast.type.UnionType;
import com.github.javaparser.ast.type.UnknownType;
import com.github.javaparser.ast.type.VoidType;
import com.github.javaparser.ast.type.WildcardType;
import com.github.javaparser.ast.visitor.Visitable;
import com.github.javaparser.utils.Pair;

import conflerge.ConflergeUtil;
import conflerge.tree.DiffResult;
import conflerge.tree.ast.NodeListWrapper;
/**
 * Performs merge operations from two DiffResults and detects conflicts, if any.
 */
@SuppressWarnings("deprecation")
public class MergeVisitor extends ModifierVisitor<Pair<DiffResult, DiffResult>> {
    
    /**
     * Visit a NodeList. This should be a NodeListWrapper, because the AST in question
     * should have been wrapped before the merge operation is performed. Perform any
     * inserts into the wrapped NodeList, then visit the list's original nodes.
     */
    @SuppressWarnings({ "rawtypes", "unchecked" })
    @Override
    public Visitable visit(NodeList n, Pair<DiffResult, DiffResult> args) {   
        
        // The NodeListWrapper visitor should ensure that all NodeLists
        // are NodeListWrappers. If not, fail.
        if (!(n instanceof NodeListWrapper)) {
            throw new IllegalStateException("Expected wrapped NodeList");
        }
        
        // Construct a Map to store any inserts that apply to this NodeList
        Map<Integer, List<Node>> inserts = new HashMap<>();
        
        // Add all the inserts from the first DiffResult
        if (args.a.listInserts.containsKey(n)) {
            Map<Integer, List<Node>> map = args.a.listInserts.get(n);
            for (Integer i : map.keySet()) {
                inserts.put(i, map.get(i));
            }
        }
        
        // Add all the inserts from the second DiffResult, failing if they overlap.
        if (args.b.listInserts.containsKey(n)) {
            Map<Integer, List<Node>> map = args.b.listInserts.get(n);
            for (Integer i : map.keySet()) {
                if (inserts.containsKey(i)) {
                    ConflergeUtil.reportConflict();
                }
                inserts.put(i, map.get(i));
            }
        }
        
        NodeList nl = ((NodeListWrapper) n).nodeList; 
        List<Node> nodes = new ArrayList<>(nl);
        nl.clear();
        
        // Perform insert operations, vist nodes.
        int i = 0;
        for (Node node : nodes) {
            if (inserts.containsKey(i)) { 
                nl.addAll(inserts.get(i));
            }
            Node item = (Node) node.accept(this, args);
            if (item != null) { 
                nl.add(item);
            }
            i++;
        }
        if (inserts.containsKey(i)) {
            nl.addAll(inserts.get(i));   
        }            
        return nl;
    }
    
    /**
     * Perform deletions or replacements rooted at this node. 
     * Dispatch a ConflictDetectionVisitor on any deleted or 
     * replaced subtree.
     * 
     * @param n
     * @param local
     * @param remote
     * @return Result of the merge operation.
     */
    private Visitable mergeOperation(Node n, DiffResult local, DiffResult remote) {       
        if (local.comments.containsKey(n) && remote.comments.containsKey(n)) {          
            ConflergeUtil.reportCommentConflict();
            Optional<Comment> localComment = local.comments.get(n);
            Optional<Comment> remoteComment = remote.comments.get(n);       
            String localContent = localComment.isPresent() ? localComment.get().getContent() : "";
            String remoteContent = remoteComment.isPresent() ? remoteComment.get().getContent() : "";
            Comment res = new BlockComment();
            res.setContent(">>> LOCAL: " + localContent + "\n<<< REMOTE: " + remoteContent);
            n.setComment(res);
        } else if (local.comments.containsKey(n)) {
            n.setComment(local.comments.get(n).orElse(null));
        } else if (remote.comments.containsKey(n)) {
            n.setComment(remote.comments.get(n).orElse(null));
        }
        
        // If local deleted or replaced this node, return the appropriate
        // value and check for modifications made by remote to the deleted 
        // or replaced subtree.
        if (local.replaced(n)) {
            n.accept(new ConflictDetectionVisitor(), remote);
            return local.replaces.get(n);
        } else if (local.deleted(n)) {
            n.accept(new ConflictDetectionVisitor(), remote);
            return null;
        }
        
        // Perform the operation above with the roles reversed.
        if (remote.replaced(n)) {
            n.accept(new ConflictDetectionVisitor(), local);
            return remote.replaces.get(n);
        } else if (remote.deleted(n)) {
            n.accept(new ConflictDetectionVisitor(), local);
            return null;
        }
        
        // If local changed the modifiers on this node, check them against remote.
        if (local.modifiers.containsKey(n)) {
            if (remote.modifiers.containsKey(n) && !remote.modifiers.get(n).equals(local.modifiers.get(n))) {
                ConflergeUtil.reportConflict();
            } else {
                ((NodeWithModifiers<?>) n).setModifiers(local.modifiers.get(n));
            }
            
        // Otherwise, add any changes made by remote.
        } else if (remote.modifiers.containsKey(n)) {
            ((NodeWithModifiers<?>) n).setModifiers(remote.modifiers.get(n));
        }
        
        return n;
    }
    
    // It would be nice to refactor the methods below, but we can't: they
    // need to call the superclass methods, which won't work if the Node
    // type is genericized.     
    
    @Override
    public Visitable visit(final AnnotationDeclaration n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final AnnotationMemberDeclaration n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ArrayAccessExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ArrayCreationExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ArrayInitializerExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final AssertStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final AssignExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final BinaryExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final BlockStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final BooleanLiteralExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final BreakStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final CastExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final CatchClause n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final CharLiteralExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ClassExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ClassOrInterfaceDeclaration n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ClassOrInterfaceType n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final CompilationUnit n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ConditionalExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ConstructorDeclaration n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ContinueStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final DoStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final DoubleLiteralExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final EmptyMemberDeclaration n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final EmptyStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final EnclosedExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final EnumConstantDeclaration n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final EnumDeclaration n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ExplicitConstructorInvocationStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ExpressionStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final FieldAccessExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final FieldDeclaration n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ForeachStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ForStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final IfStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final InitializerDeclaration n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final InstanceOfExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final IntegerLiteralExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final JavadocComment n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final LabeledStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final LongLiteralExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final MarkerAnnotationExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final MemberValuePair n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final MethodCallExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final MethodDeclaration n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final NameExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final NormalAnnotationExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final NullLiteralExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ObjectCreationExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final PackageDeclaration n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final Parameter n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final Name n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final PrimitiveType n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(SimpleName n, Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(ArrayType n, Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(ArrayCreationLevel n, Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final IntersectionType n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final UnionType n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ReturnStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final SingleMemberAnnotationExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final StringLiteralExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final SuperExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final SwitchEntryStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final SwitchStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final SynchronizedStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ThisExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final ThrowStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final TryStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final LocalClassDeclarationStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final TypeParameter n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final UnaryExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final UnknownType n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final VariableDeclarationExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final VariableDeclarator n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final VoidType n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final WhileStmt n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final WildcardType n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final LambdaExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final MethodReferenceExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final TypeExpr n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Node visit(final ImportDeclaration n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return (Node) res;
        }
    }

    @Override
    public Visitable visit(final BlockComment n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }

    @Override
    public Visitable visit(final LineComment n, final Pair<DiffResult, DiffResult> arg) {
        Visitable res = mergeOperation(n, arg.a, arg.b);
        if (res == n) {
            return super.visit(n, arg);
        } else {
            return res;
        }
    }
}